from sanic import Blueprint
from sanic.response import html, redirect

from database import fetch_all, fetch_one, execute_query
from routes.incidencias import obtener_usuario_actual, necesita_login


usuarios_bp = Blueprint("usuarios")


async def generar_username_unico(request, nombre):
    username_base = nombre.strip().lower().replace(" ", ".")
    username = username_base
    contador = 1

    while True:
        existe = await fetch_one(
            request.app,
            "SELECT id FROM usuarios WHERE username = %s",
            (username,)
        )

        if not existe:
            return username

        contador += 1
        username = f"{username_base}{contador}"


def obtener_direccion_usuarios(request):
    direccion = request.args.get("dir", "asc").lower()

    if direccion not in ("asc", "desc"):
        direccion = "asc"

    return direccion


def crear_order_by_usuarios(request):
    orden = request.args.get("orden", "nombre")
    direccion = obtener_direccion_usuarios(request)
    direccion_sql = direccion.upper()

    columnas_permitidas = {
        "nombre": "u.nombre",
        "username": "u.username",
        "email": "u.email",
        "rol": "u.rol",
        "grupo": "g.nombre",
        "semigrupo": "s.nombre"
    }

    if orden not in columnas_permitidas:
        orden = "nombre"

    columna_sql = columnas_permitidas[orden]

    order_by = f"""
    ORDER BY
        {columna_sql} {direccion_sql},
        u.nombre ASC
    """

    return order_by, orden, direccion


def crear_enlaces_orden_usuarios(ruta, orden_actual, direccion_actual):
    columnas = [
        "nombre",
        "username",
        "email",
        "rol",
        "grupo",
        "semigrupo"
    ]

    enlaces = {}

    for columna in columnas:
        if orden_actual == columna and direccion_actual == "asc":
            siguiente_direccion = "desc"
        else:
            siguiente_direccion = "asc"

        enlaces[columna] = f"{ruta}?orden={columna}&dir={siguiente_direccion}"

    return enlaces


@usuarios_bp.get("/usuarios")
async def listar_usuarios(request):
    usuario = await obtener_usuario_actual(request)

    if necesita_login(usuario):
        return redirect("/login")

    if usuario["rol"] not in ("superadmin", "admin", "tecnico"):
        return redirect("/")

    order_by, orden_actual, direccion_actual = crear_order_by_usuarios(request)

    consulta_base = f"""
        SELECT 
            u.id,
            u.nombre,
            u.username,
            u.email,
            u.rol,
            u.grupo_id,
            u.semigrupo_id,
            g.nombre AS grupo,
            s.nombre AS semigrupo
        FROM usuarios u
        LEFT JOIN grupos g ON u.grupo_id = g.id
        LEFT JOIN semigrupos s ON u.semigrupo_id = s.id
    """

    if usuario["rol"] == "superadmin":
        usuarios = await fetch_all(
            request.app,
            consulta_base + f"""
            {order_by}
            """
        )

    elif usuario["rol"] == "admin":
        usuarios = await fetch_all(
            request.app,
            consulta_base + f"""
            WHERE u.grupo_id = %s
            OR u.rol = 'cliente'
            {order_by}
            """,
            (usuario["grupo_id"],)
        )

    else:
        usuarios = await fetch_all(
            request.app,
            consulta_base + f"""
            WHERE u.rol = 'cliente'
            {order_by}
            """
        )

    grupos = await fetch_all(
        request.app,
        """
        SELECT id, codigo, nombre
        FROM grupos
        ORDER BY nombre
        """
    )

    semigrupos = await fetch_all(
        request.app,
        """
        SELECT id, codigo, nombre, grupo_id
        FROM semigrupos
        ORDER BY grupo_id, nombre
        """
    )

    template = request.app.ctx.templates.get_template("usuarios.html")

    return html(template.render(
        usuario=usuario,
        usuarios=usuarios,
        grupos=grupos,
        semigrupos=semigrupos,
        enlaces_orden=crear_enlaces_orden_usuarios(
            "/usuarios",
            orden_actual,
            direccion_actual
        ),
        orden_actual=orden_actual,
        direccion_actual=direccion_actual,
        error=None
    ))


@usuarios_bp.post("/crear-usuario")
async def crear_usuario(request):
    usuario = await obtener_usuario_actual(request)

    if necesita_login(usuario):
        return redirect("/login")

    if usuario["rol"] not in ("superadmin", "admin", "tecnico"):
        return redirect("/")

    nombre = request.form.get("nombre", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "").strip()
    rol_nuevo = request.form.get("rol", "").strip()
    grupo_id = request.form.get("grupo_id")
    semigrupo_id = request.form.get("semigrupo_id")

    if not nombre or not email or not password or not rol_nuevo:
        return redirect("/usuarios")

    if usuario["rol"] == "tecnico" and rol_nuevo != "cliente":
        return redirect("/usuarios")

    if usuario["rol"] == "admin" and rol_nuevo not in ("tecnico", "cliente"):
        return redirect("/usuarios")

    if usuario["rol"] == "superadmin" and rol_nuevo not in ("admin", "tecnico", "cliente"):
        return redirect("/usuarios")

    email_existe = await fetch_one(
        request.app,
        "SELECT id FROM usuarios WHERE email = %s",
        (email,)
    )

    if email_existe:
        return redirect("/usuarios")

    username = await generar_username_unico(request, nombre)

    if rol_nuevo == "cliente":
        grupo_final = None
        semigrupo_final = None

    elif usuario["rol"] == "superadmin":
        grupo_final = grupo_id
        semigrupo_final = semigrupo_id

        semigrupo_correcto = await fetch_one(
            request.app,
            """
            SELECT id
            FROM semigrupos
            WHERE id = %s
            AND grupo_id = %s
            """,
            (semigrupo_final, grupo_final)
        )

        if not semigrupo_correcto:
            return redirect("/usuarios")

    else:
        grupo_final = usuario["grupo_id"]
        semigrupo_final = semigrupo_id

        semigrupo_correcto = await fetch_one(
            request.app,
            """
            SELECT id
            FROM semigrupos
            WHERE id = %s
            AND grupo_id = %s
            """,
            (semigrupo_final, grupo_final)
        )

        if not semigrupo_correcto:
            return redirect("/usuarios")

    await execute_query(
        request.app,
        """
        INSERT INTO usuarios 
        (nombre, username, email, password, rol, grupo_id, semigrupo_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            nombre,
            username,
            email,
            password,
            rol_nuevo,
            grupo_final,
            semigrupo_final
        )
    )

    return redirect("/usuarios")


@usuarios_bp.post("/usuario/<id:int>/actualizar-asignacion")
async def actualizar_asignacion_usuario(request, id):
    usuario = await obtener_usuario_actual(request)

    if necesita_login(usuario):
        return redirect("/login")

    if usuario["rol"] != "superadmin":
        return redirect("/usuarios")

    usuario_editado = await fetch_one(
        request.app,
        """
        SELECT id, rol
        FROM usuarios
        WHERE id = %s
        """,
        (id,)
    )

    if not usuario_editado:
        return redirect("/usuarios")

    if usuario_editado["rol"] not in ("admin", "tecnico"):
        return redirect("/usuarios")

    grupo_id = request.form.get("grupo_id")
    semigrupo_id = request.form.get("semigrupo_id")

    semigrupo_correcto = await fetch_one(
        request.app,
        """
        SELECT id
        FROM semigrupos
        WHERE id = %s
        AND grupo_id = %s
        """,
        (semigrupo_id, grupo_id)
    )

    if not semigrupo_correcto:
        return redirect("/usuarios")

    await execute_query(
        request.app,
        """
        UPDATE usuarios
        SET grupo_id = %s,
            semigrupo_id = %s
        WHERE id = %s
        """,
        (grupo_id, semigrupo_id, id)
    )

    return redirect("/usuarios")