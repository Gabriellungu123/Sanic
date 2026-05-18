import random
import string

from sanic import Blueprint
from sanic.response import html, redirect

from database import fetch_all, fetch_one, execute_query


incidencias_bp = Blueprint("incidencias")


ESTADOS_CON_COMENTARIO_OBLIGATORIO = (
    "Pendiente",
    "Cerrado",
    "Cancelado",
    "Resuelta"
)


def generar_codigo():
    letras = string.ascii_uppercase
    numeros = string.digits
    return "INC-" + "".join(random.choices(letras + numeros, k=6))


async def generar_codigo_unico(request):
    while True:
        codigo = generar_codigo()

        existe = await fetch_one(
            request.app,
            "SELECT id FROM incidencias WHERE codigo = %s",
            (codigo,)
        )

        if not existe:
            return codigo


async def obtener_usuario_actual(request):
    user_id = request.cookies.get("user_id")

    if not user_id:
        return None

    usuario = await fetch_one(
        request.app,
        """
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
        WHERE u.id = %s
        """,
        (user_id,)
    )

    return usuario


def necesita_login(usuario):
    return usuario is None


def obtener_direccion(request):
    direccion = request.args.get("dir", "desc").lower()

    if direccion not in ("asc", "desc"):
        direccion = "desc"

    return direccion


def crear_enlaces_orden(ruta, orden_actual, direccion_actual):
    columnas = [
        "codigo",
        "resumen",
        "estado",
        "prioridad",
        "grupo",
        "semigrupo",
        "cliente",
        "tecnico"
    ]

    enlaces = {}

    for columna in columnas:
        if orden_actual == columna and direccion_actual == "asc":
            siguiente_direccion = "desc"
        else:
            siguiente_direccion = "asc"

        enlaces[columna] = f"{ruta}?orden={columna}&dir={siguiente_direccion}"

    return enlaces


def crear_order_by(request, usuario=None, ordenar_tecnico_propio=False):
    orden = request.args.get("orden", "fecha")
    direccion = obtener_direccion(request)
    direccion_sql = direccion.upper()

    columnas_permitidas = {
        "codigo": "i.codigo",
        "resumen": "i.resumen",
        "estado": "i.estado",
        "prioridad": "FIELD(i.prioridad, 'Baja', 'Media', 'Alta', 'Urgente')",
        "grupo": "g.nombre",
        "semigrupo": "s.nombre",
        "cliente": "cliente.nombre",
        "tecnico": "tecnico.nombre"
    }

    if orden == "tecnico" and ordenar_tecnico_propio and usuario and usuario["rol"] == "tecnico":
        order_by = """
        ORDER BY
            CASE
                WHEN i.tecnico_id = %s THEN 0
                ELSE 1
            END,
            tecnico.nombre ASC,
            i.id DESC
        """
        parametros_extra = (usuario["id"],)

        return order_by, parametros_extra, orden, direccion

    if orden in columnas_permitidas:
        columna_sql = columnas_permitidas[orden]

        order_by = f"""
        ORDER BY
            {columna_sql} {direccion_sql},
            i.id DESC
        """

        return order_by, (), orden, direccion

    return "ORDER BY i.id DESC", (), "fecha", "desc"


def usuario_puede_ver_incidencia(usuario, incidencia):
    if usuario["rol"] == "superadmin":
        return True

    if usuario["rol"] == "cliente" and incidencia["cliente_id"] == usuario["id"]:
        return True

    if usuario["rol"] in ("tecnico", "admin"):
        return True

    return False


def usuario_puede_comentar_incidencia(usuario, incidencia):
    if usuario["rol"] == "superadmin":
        return True

    if usuario["rol"] == "cliente" and incidencia["cliente_id"] == usuario["id"]:
        return True

    if usuario["rol"] in ("tecnico", "admin") and incidencia["grupo_id"] == usuario["grupo_id"]:
        return True

    return False


def usuario_puede_modificar_incidencia(usuario, incidencia):
    if usuario["rol"] == "superadmin":
        return True

    if usuario["rol"] in ("tecnico", "admin") and incidencia["grupo_id"] == usuario["grupo_id"]:
        return True

    return False


async def obtener_incidencias_para_usuario(request, usuario):
    order_by, parametros_extra, orden_actual, direccion_actual = crear_order_by(
        request,
        usuario,
        ordenar_tecnico_propio=True
    )

    consulta_base = """
        SELECT 
            i.id,
            i.codigo,
            i.resumen,
            i.descripcion,
            i.contacto,
            i.estado,
            i.prioridad,
            i.comentario_cliente_pendiente,
            i.fecha_creacion,
            i.fecha_actualizacion,
            g.nombre AS grupo,
            s.nombre AS semigrupo,
            cliente.nombre AS cliente,
            tecnico.nombre AS tecnico
        FROM incidencias i
        INNER JOIN grupos g ON i.grupo_id = g.id
        INNER JOIN semigrupos s ON i.semigrupo_id = s.id
        INNER JOIN usuarios cliente ON i.cliente_id = cliente.id
        LEFT JOIN usuarios tecnico ON i.tecnico_id = tecnico.id
    """

    if usuario["rol"] == "superadmin":
        incidencias = await fetch_all(
            request.app,
            consulta_base + f"""
            WHERE i.estado IN ('Asignado', 'En curso', 'Pendiente')
            {order_by}
            """,
            parametros_extra
        )

    elif usuario["rol"] == "cliente":
        incidencias = await fetch_all(
            request.app,
            consulta_base + f"""
            WHERE i.cliente_id = %s
            AND i.estado IN ('Asignado', 'En curso', 'Pendiente')
            {order_by}
            """,
            (usuario["id"],) + parametros_extra
        )

    elif usuario["rol"] == "tecnico":
        incidencias = await fetch_all(
            request.app,
            consulta_base + f"""
            WHERE i.tecnico_id = %s
            AND i.estado IN ('Asignado', 'En curso', 'Pendiente')
            {order_by}
            """,
            (usuario["id"],) + parametros_extra
        )

    else:
        incidencias = await fetch_all(
            request.app,
            consulta_base + f"""
            WHERE i.grupo_id = %s
            AND i.estado IN ('Asignado', 'En curso', 'Pendiente')
            {order_by}
            """,
            (usuario["grupo_id"],) + parametros_extra
        )

    return incidencias, orden_actual, direccion_actual


@incidencias_bp.get("/")
async def inicio(request):
    usuario = await obtener_usuario_actual(request)

    if necesita_login(usuario):
        return redirect("/login")

    incidencias, orden_actual, direccion_actual = await obtener_incidencias_para_usuario(
        request,
        usuario
    )

    template = request.app.ctx.templates.get_template("index.html")

    return html(template.render(
        usuario=usuario,
        incidencias=incidencias,
        total=len(incidencias),
        enlaces_orden=crear_enlaces_orden(
            "/",
            orden_actual,
            direccion_actual
        ),
        orden_actual=orden_actual,
        direccion_actual=direccion_actual
    ))


@incidencias_bp.get("/crear-incidencia")
async def formulario_crear_incidencia(request):
    usuario = await obtener_usuario_actual(request)

    if necesita_login(usuario):
        return redirect("/login")

    grupos = await fetch_all(
        request.app,
        "SELECT * FROM grupos ORDER BY nombre"
    )

    semigrupos = await fetch_all(
        request.app,
        "SELECT * FROM semigrupos ORDER BY grupo_id, nombre"
    )

    solicitantes = await fetch_all(
        request.app,
        """
        SELECT 
            u.id,
            u.nombre,
            u.username,
            u.rol,
            g.nombre AS grupo,
            s.nombre AS semigrupo
        FROM usuarios u
        LEFT JOIN grupos g ON u.grupo_id = g.id
        LEFT JOIN semigrupos s ON u.semigrupo_id = s.id
        WHERE u.rol = 'cliente'
        ORDER BY u.nombre
        """
    )

    template = request.app.ctx.templates.get_template("crear_incidencia.html")

    return html(template.render(
        usuario=usuario,
        grupos=grupos,
        semigrupos=semigrupos,
        solicitantes=solicitantes
    ))


@incidencias_bp.post("/crear-incidencia")
async def crear_incidencia(request):
    usuario = await obtener_usuario_actual(request)

    if necesita_login(usuario):
        return redirect("/login")

    resumen = request.form.get("resumen", "").strip()
    descripcion = request.form.get("descripcion", "").strip()
    contacto = request.form.get("contacto", "").strip()
    prioridad = request.form.get("prioridad", "Media")
    grupo_id = request.form.get("grupo_id")
    semigrupo_id = request.form.get("semigrupo_id")

    cliente_id = usuario["id"]

    if usuario["rol"] in ("superadmin", "admin", "tecnico"):
        solicitante = request.form.get("solicitante", "").strip()

        if solicitante:
            try:
                cliente_id = int(solicitante.split(" - ")[0])
            except Exception:
                cliente_id = usuario["id"]

    codigo = await generar_codigo_unico(request)

    nueva_id = await execute_query(
        request.app,
        """
        INSERT INTO incidencias 
        (
            codigo,
            resumen,
            descripcion,
            contacto,
            prioridad,
            cliente_id,
            grupo_id,
            semigrupo_id,
            tecnico_id,
            estado
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NULL, 'Pendiente')
        """,
        (
            codigo,
            resumen,
            descripcion,
            contacto,
            prioridad,
            cliente_id,
            grupo_id,
            semigrupo_id
        )
    )

    await execute_query(
        request.app,
        """
        INSERT INTO comentarios (incidencia_id, usuario_id, comentario)
        VALUES (%s, %s, %s)
        """,
        (
            nueva_id,
            usuario["id"],
            "Incidencia creada."
        )
    )

    return redirect("/")


@incidencias_bp.get("/incidencias-grupo")
async def incidencias_grupo(request):
    usuario = await obtener_usuario_actual(request)

    if necesita_login(usuario):
        return redirect("/login")

    if usuario["rol"] == "cliente":
        return redirect("/")

    order_by, parametros_extra, orden_actual, direccion_actual = crear_order_by(
        request,
        usuario,
        ordenar_tecnico_propio=True
    )

    consulta_base = """
        SELECT 
            i.id,
            i.codigo,
            i.resumen,
            i.descripcion,
            i.contacto,
            i.estado,
            i.prioridad,
            i.comentario_cliente_pendiente,
            i.fecha_creacion,
            g.nombre AS grupo,
            s.nombre AS semigrupo,
            cliente.nombre AS cliente,
            tecnico.nombre AS tecnico
        FROM incidencias i
        INNER JOIN grupos g ON i.grupo_id = g.id
        INNER JOIN semigrupos s ON i.semigrupo_id = s.id
        INNER JOIN usuarios cliente ON i.cliente_id = cliente.id
        LEFT JOIN usuarios tecnico ON i.tecnico_id = tecnico.id
    """

    if usuario["rol"] == "superadmin":
        incidencias = await fetch_all(
            request.app,
            consulta_base + f"""
            WHERE i.estado IN ('Asignado', 'En curso', 'Pendiente')
            {order_by}
            """,
            parametros_extra
        )
    else:
        incidencias = await fetch_all(
            request.app,
            consulta_base + f"""
            WHERE i.grupo_id = %s
            AND i.estado IN ('Asignado', 'En curso', 'Pendiente')
            {order_by}
            """,
            (usuario["grupo_id"],) + parametros_extra
        )

    template = request.app.ctx.templates.get_template("incidencias.html")

    return html(template.render(
        usuario=usuario,
        incidencias=incidencias,
        total=len(incidencias),
        titulo_pagina="Incidencias activas",
        enlaces_orden=crear_enlaces_orden(
            "/incidencias-grupo",
            orden_actual,
            direccion_actual
        ),
        orden_actual=orden_actual,
        direccion_actual=direccion_actual
    ))


@incidencias_bp.get("/incidencias-archivadas")
async def incidencias_archivadas(request):
    usuario = await obtener_usuario_actual(request)

    if necesita_login(usuario):
        return redirect("/login")

    order_by, parametros_extra, orden_actual, direccion_actual = crear_order_by(
        request,
        usuario,
        ordenar_tecnico_propio=False
    )

    consulta_base = """
        SELECT 
            i.id,
            i.codigo,
            i.resumen,
            i.estado,
            i.prioridad,
            i.comentario_cliente_pendiente,
            g.nombre AS grupo,
            s.nombre AS semigrupo,
            cliente.nombre AS cliente,
            tecnico.nombre AS tecnico
        FROM incidencias i
        INNER JOIN grupos g ON i.grupo_id = g.id
        INNER JOIN semigrupos s ON i.semigrupo_id = s.id
        INNER JOIN usuarios cliente ON i.cliente_id = cliente.id
        LEFT JOIN usuarios tecnico ON i.tecnico_id = tecnico.id
    """

    if usuario["rol"] == "superadmin":
        incidencias = await fetch_all(
            request.app,
            consulta_base + f"""
            WHERE i.estado IN ('Cerrado', 'Cancelado', 'Resuelta')
            {order_by}
            """,
            parametros_extra
        )

    elif usuario["rol"] == "cliente":
        incidencias = await fetch_all(
            request.app,
            consulta_base + f"""
            WHERE i.cliente_id = %s
            AND i.estado IN ('Cerrado', 'Cancelado', 'Resuelta')
            {order_by}
            """,
            (usuario["id"],) + parametros_extra
        )

    elif usuario["rol"] == "tecnico":
        incidencias = await fetch_all(
            request.app,
            consulta_base + f"""
            WHERE i.tecnico_id = %s
            AND i.estado IN ('Cerrado', 'Cancelado', 'Resuelta')
            {order_by}
            """,
            (usuario["id"],) + parametros_extra
        )

    else:
        incidencias = await fetch_all(
            request.app,
            consulta_base + f"""
            WHERE i.grupo_id = %s
            AND i.estado IN ('Cerrado', 'Cancelado', 'Resuelta')
            {order_by}
            """,
            (usuario["grupo_id"],) + parametros_extra
        )

    template = request.app.ctx.templates.get_template("incidencias.html")

    return html(template.render(
        usuario=usuario,
        incidencias=incidencias,
        total=len(incidencias),
        titulo_pagina="Incidencias archivadas",
        enlaces_orden=crear_enlaces_orden(
            "/incidencias-archivadas",
            orden_actual,
            direccion_actual
        ),
        orden_actual=orden_actual,
        direccion_actual=direccion_actual
    ))


@incidencias_bp.post("/buscar-incidencia")
async def buscar_incidencia(request):
    usuario = await obtener_usuario_actual(request)

    if necesita_login(usuario):
        return redirect("/login")

    codigo = request.form.get("codigo", "").strip().upper()

    return redirect(f"/incidencia/{codigo}")


@incidencias_bp.get("/incidencia/<codigo>")
async def detalle_incidencia(request, codigo):
    usuario = await obtener_usuario_actual(request)

    if necesita_login(usuario):
        return redirect("/login")

    codigo = codigo.strip().upper()

    incidencia = await fetch_one(
        request.app,
        """
        SELECT 
            i.id,
            i.codigo,
            i.resumen,
            i.descripcion,
            i.contacto,
            i.estado,
            i.prioridad,
            i.comentario_cliente_pendiente,
            i.fecha_creacion,
            i.fecha_actualizacion,
            i.cliente_id,
            i.tecnico_id,
            i.grupo_id,
            i.semigrupo_id,
            g.nombre AS grupo,
            s.nombre AS semigrupo,
            cliente.nombre AS cliente,
            tecnico.nombre AS tecnico
        FROM incidencias i
        INNER JOIN grupos g ON i.grupo_id = g.id
        INNER JOIN semigrupos s ON i.semigrupo_id = s.id
        INNER JOIN usuarios cliente ON i.cliente_id = cliente.id
        LEFT JOIN usuarios tecnico ON i.tecnico_id = tecnico.id
        WHERE i.codigo = %s
        """,
        (codigo,)
    )

    if not incidencia:
        return redirect("/")

    if not usuario_puede_ver_incidencia(usuario, incidencia):
        return redirect("/")

    if usuario["rol"] in ("superadmin", "admin", "tecnico"):
        await execute_query(
            request.app,
            """
            UPDATE incidencias
            SET comentario_cliente_pendiente = 0
            WHERE id = %s
            """,
            (incidencia["id"],)
        )

    comentarios = await fetch_all(
        request.app,
        """
        SELECT 
            c.comentario,
            c.fecha_creacion,
            u.nombre AS usuario,
            u.rol
        FROM comentarios c
        INNER JOIN usuarios u ON c.usuario_id = u.id
        WHERE c.incidencia_id = %s
        ORDER BY c.id ASC
        """,
        (incidencia["id"],)
    )

    puede_comentar = usuario_puede_comentar_incidencia(usuario, incidencia)
    puede_modificar = usuario_puede_modificar_incidencia(usuario, incidencia)

    grupos = await fetch_all(
        request.app,
        "SELECT * FROM grupos ORDER BY nombre"
    )

    semigrupos = await fetch_all(
        request.app,
        """
        SELECT id, codigo, nombre, grupo_id
        FROM semigrupos
        ORDER BY grupo_id, nombre
        """
    )

    tecnicos = await fetch_all(
        request.app,
        """
        SELECT 
            id,
            nombre,
            username,
            grupo_id,
            semigrupo_id
        FROM usuarios
        WHERE rol = 'tecnico'
        ORDER BY grupo_id, nombre
        """
    )

    template = request.app.ctx.templates.get_template("detalle_incidencia.html")

    return html(template.render(
        usuario=usuario,
        incidencia=incidencia,
        comentarios=comentarios,
        puede_comentar=puede_comentar,
        puede_modificar=puede_modificar,
        grupos=grupos,
        semigrupos=semigrupos,
        tecnicos=tecnicos,
        error=None
    ))


@incidencias_bp.post("/incidencia/<codigo>/guardar-cambios")
async def guardar_cambios_incidencia(request, codigo):
    usuario = await obtener_usuario_actual(request)

    if necesita_login(usuario):
        return redirect("/login")

    codigo = codigo.strip().upper()

    incidencia = await fetch_one(
        request.app,
        """
        SELECT 
            id,
            cliente_id,
            grupo_id,
            semigrupo_id,
            tecnico_id,
            estado
        FROM incidencias
        WHERE codigo = %s
        """,
        (codigo,)
    )

    if not incidencia:
        return redirect("/")

    if not usuario_puede_modificar_incidencia(usuario, incidencia):
        return redirect("/")

    nuevo_estado = request.form.get("estado")
    nuevo_grupo_id = request.form.get("grupo_id")
    nuevo_semigrupo_id = request.form.get("semigrupo_id")
    nuevo_tecnico_id = request.form.get("tecnico_id")
    comentario_usuario = request.form.get("comentario", "").strip()

    if nuevo_tecnico_id == "":
        nuevo_tecnico_id = None

    if nuevo_semigrupo_id == "":
        nuevo_semigrupo_id = None

    if nuevo_estado in ESTADOS_CON_COMENTARIO_OBLIGATORIO and not comentario_usuario:
        return redirect(f"/incidencia/{codigo}")

    if nuevo_semigrupo_id:
        semigrupo_correcto = await fetch_one(
            request.app,
            """
            SELECT id
            FROM semigrupos
            WHERE id = %s
            AND grupo_id = %s
            """,
            (nuevo_semigrupo_id, nuevo_grupo_id)
        )

        if not semigrupo_correcto:
            return redirect(f"/incidencia/{codigo}")
    else:
        semigrupo_actual_valido = await fetch_one(
            request.app,
            """
            SELECT id
            FROM semigrupos
            WHERE id = %s
            AND grupo_id = %s
            """,
            (incidencia["semigrupo_id"], nuevo_grupo_id)
        )

        if semigrupo_actual_valido:
            nuevo_semigrupo_id = incidencia["semigrupo_id"]
        else:
            primer_semigrupo = await fetch_one(
                request.app,
                """
                SELECT id
                FROM semigrupos
                WHERE grupo_id = %s
                ORDER BY nombre
                LIMIT 1
                """,
                (nuevo_grupo_id,)
            )

            if not primer_semigrupo:
                return redirect(f"/incidencia/{codigo}")

            nuevo_semigrupo_id = primer_semigrupo["id"]

    if nuevo_tecnico_id:
        tecnico_correcto = await fetch_one(
            request.app,
            """
            SELECT id
            FROM usuarios
            WHERE id = %s
            AND rol = 'tecnico'
            AND grupo_id = %s
            """,
            (nuevo_tecnico_id, nuevo_grupo_id)
        )

        if not tecnico_correcto:
            return redirect(f"/incidencia/{codigo}")

    await execute_query(
        request.app,
        """
        UPDATE incidencias
        SET estado = %s,
            grupo_id = %s,
            semigrupo_id = %s,
            tecnico_id = %s
        WHERE codigo = %s
        """,
        (
            nuevo_estado,
            nuevo_grupo_id,
            nuevo_semigrupo_id,
            nuevo_tecnico_id,
            codigo
        )
    )

    grupo = await fetch_one(
        request.app,
        "SELECT nombre FROM grupos WHERE id = %s",
        (nuevo_grupo_id,)
    )

    semigrupo = await fetch_one(
        request.app,
        "SELECT nombre FROM semigrupos WHERE id = %s",
        (nuevo_semigrupo_id,)
    )

    tecnico_nombre = "Sin tecnico asignado"

    if nuevo_tecnico_id:
        tecnico = await fetch_one(
            request.app,
            "SELECT nombre FROM usuarios WHERE id = %s",
            (nuevo_tecnico_id,)
        )

        if tecnico:
            tecnico_nombre = tecnico["nombre"]

    comentario_sistema = (
        f"Cambios guardados. Estado: {nuevo_estado}. "
        f"Grupo: {grupo['nombre']}. "
        f"Semigrupo: {semigrupo['nombre']}. "
        f"Tecnico: {tecnico_nombre}."
    )

    if comentario_usuario:
        comentario_sistema += f" Comentario: {comentario_usuario}"

    await execute_query(
        request.app,
        """
        INSERT INTO comentarios (incidencia_id, usuario_id, comentario)
        VALUES (%s, %s, %s)
        """,
        (
            incidencia["id"],
            usuario["id"],
            comentario_sistema
        )
    )

    return redirect(f"/incidencia/{codigo}")


@incidencias_bp.post("/incidencia/<codigo>/comentario")
async def crear_comentario(request, codigo):
    usuario = await obtener_usuario_actual(request)

    if necesita_login(usuario):
        return redirect("/login")

    codigo = codigo.strip().upper()

    incidencia = await fetch_one(
        request.app,
        """
        SELECT id, cliente_id, grupo_id
        FROM incidencias 
        WHERE codigo = %s
        """,
        (codigo,)
    )

    if not incidencia:
        return redirect("/")

    if not usuario_puede_comentar_incidencia(usuario, incidencia):
        return redirect("/")

    comentario = request.form.get("comentario", "").strip()

    if not comentario:
        return redirect(f"/incidencia/{codigo}")

    await execute_query(
        request.app,
        """
        INSERT INTO comentarios (incidencia_id, usuario_id, comentario)
        VALUES (%s, %s, %s)
        """,
        (incidencia["id"], usuario["id"], comentario)
    )

    if usuario["rol"] == "cliente":
        await execute_query(
            request.app,
            """
            UPDATE incidencias
            SET comentario_cliente_pendiente = 1
            WHERE id = %s
            """,
            (incidencia["id"],)
        )

    return redirect(f"/incidencia/{codigo}")


@incidencias_bp.post("/borrar-incidencia/<id:int>")
async def borrar_incidencia(request, id):
    usuario = await obtener_usuario_actual(request)

    if necesita_login(usuario):
        return redirect("/login")

    if usuario["rol"] not in ("superadmin", "admin"):
        return redirect("/")

    incidencia = await fetch_one(
        request.app,
        """
        SELECT id, grupo_id
        FROM incidencias
        WHERE id = %s
        """,
        (id,)
    )

    if not incidencia:
        return redirect("/")

    if usuario["rol"] == "admin" and incidencia["grupo_id"] != usuario["grupo_id"]:
        return redirect("/")

    await execute_query(
        request.app,
        "DELETE FROM comentarios WHERE incidencia_id = %s",
        (id,)
    )

    await execute_query(
        request.app,
        "DELETE FROM incidencias WHERE id = %s",
        (id,)
    )

    return redirect("/")