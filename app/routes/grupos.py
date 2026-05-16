import random
import string

from sanic import Blueprint
from sanic.response import html, redirect

from database import fetch_all, fetch_one, execute_query
from routes.incidencias import obtener_usuario_actual, necesita_login


grupos_bp = Blueprint("grupos")


def generar_codigo(prefijo):
    letras = string.ascii_uppercase
    numeros = string.digits

    return prefijo + "-" + "".join(
        random.choices(letras + numeros, k=5)
    )


async def generar_codigo_unico(request, tabla, prefijo):
    while True:
        codigo = generar_codigo(prefijo)

        existe = await fetch_one(
            request.app,
            f"SELECT id FROM {tabla} WHERE codigo = %s",
            (codigo,)
        )

        if not existe:
            return codigo


@grupos_bp.get("/grupos")
async def listar_grupos(request):
    usuario = await obtener_usuario_actual(request)

    if necesita_login(usuario):
        return redirect("/login")

    if usuario["rol"] not in ("admin", "superadmin"):
        return redirect("/")

    grupos = await fetch_all(
        request.app,
        """
        SELECT 
            g.id,
            g.codigo,
            g.nombre,
            COUNT(DISTINCT s.id) AS total_semigrupos,
            COUNT(DISTINCT u.id) AS total_usuarios
        FROM grupos g
        LEFT JOIN semigrupos s 
            ON s.grupo_id = g.id
        LEFT JOIN usuarios u 
            ON u.grupo_id = g.id
        GROUP BY g.id, g.codigo, g.nombre
        ORDER BY g.id ASC
        """
    )

    semigrupos = await fetch_all(
        request.app,
        """
        SELECT 
            s.id,
            s.codigo,
            s.nombre,
            s.grupo_id,
            g.nombre AS grupo
        FROM semigrupos s
        INNER JOIN grupos g 
            ON s.grupo_id = g.id
        ORDER BY g.id ASC, s.id ASC
        """
    )

    tecnicos = await fetch_all(
        request.app,
        """
        SELECT 
            u.id,
            u.nombre,
            u.username,
            u.email,
            u.rol,
            u.grupo_id,
            g.nombre AS grupo,
            GROUP_CONCAT(
                DISTINCT s.nombre
                ORDER BY s.nombre
                SEPARATOR ', '
            ) AS semigrupos

        FROM usuarios u

        LEFT JOIN grupos g 
            ON u.grupo_id = g.id

        LEFT JOIN incidencias i 
            ON i.tecnico_id = u.id

        LEFT JOIN semigrupos s 
            ON i.semigrupo_id = s.id

        WHERE u.rol = 'tecnico'

        GROUP BY
            u.id,
            u.nombre,
            u.username,
            u.email,
            u.rol,
            u.grupo_id,
            g.nombre

        ORDER BY u.nombre ASC
        """
    )

    admins = await fetch_all(
        request.app,
        """
        SELECT 
            u.id,
            u.nombre,
            u.username,
            u.email,
            u.rol,
            u.grupo_id,
            g.nombre AS grupo

        FROM usuarios u

        LEFT JOIN grupos g 
            ON u.grupo_id = g.id

        WHERE u.rol = 'admin'

        ORDER BY g.nombre ASC, u.nombre ASC
        """
    )

    tecnicos_mi_grupo = []

    if usuario["rol"] == "admin":
        tecnicos_mi_grupo = await fetch_all(
            request.app,
            """
            SELECT 
                u.id,
                u.nombre,
                u.username,
                u.email,
                u.grupo_id,
                g.nombre AS grupo,

                GROUP_CONCAT(
                    DISTINCT s.nombre
                    ORDER BY s.nombre
                    SEPARATOR ', '
                ) AS semigrupos

            FROM usuarios u

            LEFT JOIN grupos g 
                ON u.grupo_id = g.id

            LEFT JOIN incidencias i 
                ON i.tecnico_id = u.id

            LEFT JOIN semigrupos s 
                ON i.semigrupo_id = s.id

            WHERE u.rol = 'tecnico'
            AND u.grupo_id = %s

            GROUP BY
                u.id,
                u.nombre,
                u.username,
                u.email,
                u.grupo_id,
                g.nombre

            ORDER BY u.nombre ASC
            """,
            (usuario["grupo_id"],)
        )

    template = request.app.ctx.templates.get_template("grupos.html")

    return html(template.render(
        usuario=usuario,
        grupos=grupos,
        semigrupos=semigrupos,
        tecnicos=tecnicos,
        admins=admins,
        tecnicos_mi_grupo=tecnicos_mi_grupo
    ))


@grupos_bp.post("/crear-grupo")
async def crear_grupo(request):
    usuario = await obtener_usuario_actual(request)

    if necesita_login(usuario):
        return redirect("/login")

    if usuario["rol"] not in ("admin", "superadmin"):
        return redirect("/grupos")

    nombre = request.form.get("nombre", "").strip()
    tecnico_id = request.form.get("tecnico_id")

    if not nombre or not tecnico_id:
        return redirect("/grupos")

    tecnico = await fetch_one(
        request.app,
        """
        SELECT id
        FROM usuarios
        WHERE id = %s
        AND rol = 'tecnico'
        """,
        (tecnico_id,)
    )

    if not tecnico:
        return redirect("/grupos")

    codigo = await generar_codigo_unico(
        request,
        "grupos",
        "GRP"
    )

    nuevo_grupo_id = await execute_query(
        request.app,
        """
        INSERT INTO grupos (codigo, nombre)
        VALUES (%s, %s)
        """,
        (codigo, nombre)
    )

    await execute_query(
        request.app,
        """
        UPDATE usuarios
        SET rol = 'admin',
            grupo_id = %s
        WHERE id = %s
        """,
        (nuevo_grupo_id, tecnico_id)
    )

    return redirect("/grupos")


@grupos_bp.post("/crear-semigrupo")
async def crear_semigrupo(request):
    usuario = await obtener_usuario_actual(request)

    if necesita_login(usuario):
        return redirect("/login")

    if usuario["rol"] not in ("admin", "superadmin"):
        return redirect("/grupos")

    nombre = request.form.get("nombre", "").strip()
    grupo_id = request.form.get("grupo_id")

    if not nombre or not grupo_id:
        return redirect("/grupos")

    grupo = await fetch_one(
        request.app,
        """
        SELECT id
        FROM grupos
        WHERE id = %s
        """,
        (grupo_id,)
    )

    if not grupo:
        return redirect("/grupos")

    codigo = await generar_codigo_unico(
        request,
        "semigrupos",
        "SEM"
    )

    await execute_query(
        request.app,
        """
        INSERT INTO semigrupos
        (
            codigo,
            nombre,
            grupo_id
        )
        VALUES (%s, %s, %s)
        """,
        (
            codigo,
            nombre,
            grupo_id
        )
    )

    return redirect("/grupos")


@grupos_bp.post("/ascender-tecnico")
async def ascender_tecnico(request):
    usuario = await obtener_usuario_actual(request)

    if necesita_login(usuario):
        return redirect("/login")

    if usuario["rol"] not in ("admin", "superadmin"):
        return redirect("/grupos")

    tecnico_id = request.form.get("tecnico_id")

    if not tecnico_id:
        return redirect("/grupos")

    if usuario["rol"] == "admin":
        tecnico = await fetch_one(
            request.app,
            """
            SELECT id
            FROM usuarios
            WHERE id = %s
            AND rol = 'tecnico'
            AND grupo_id = %s
            """,
            (
                tecnico_id,
                usuario["grupo_id"]
            )
        )
    else:
        tecnico = await fetch_one(
            request.app,
            """
            SELECT id
            FROM usuarios
            WHERE id = %s
            AND rol = 'tecnico'
            """,
            (tecnico_id,)
        )

    if not tecnico:
        return redirect("/grupos")

    await execute_query(
        request.app,
        """
        UPDATE usuarios
        SET rol = 'admin'
        WHERE id = %s
        """,
        (tecnico_id,)
    )

    return redirect("/grupos")