from sanic import Blueprint
from sanic.response import html, redirect

from database import fetch_one


auth_bp = Blueprint("auth")


@auth_bp.get("/login")
async def login_formulario(request):
    template = request.app.ctx.templates.get_template("login.html")
    return html(template.render(error=None))


@auth_bp.post("/login")
async def login(request):
    username = request.form.get("username")
    password = request.form.get("password")

    usuario = await fetch_one(
        request.app,
        """
        SELECT id, nombre, username, email, rol, grupo_id
        FROM usuarios
        WHERE username = %s AND password = %s
        """,
        (username, password)
    )

    if not usuario:
        template = request.app.ctx.templates.get_template("login.html")
        return html(template.render(error="Usuario o contrasena incorrectos"))

    respuesta = redirect("/")

    respuesta.add_cookie(
        "user_id",
        str(usuario["id"]),
        httponly=True,
        path="/"
    )

    return respuesta


@auth_bp.get("/logout")
async def logout(request):
    respuesta = redirect("/login")

    respuesta.delete_cookie(
        "user_id",
        path="/"
    )

    return respuesta