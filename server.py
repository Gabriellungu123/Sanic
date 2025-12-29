# server.py
from sanic import Sanic, response
from sanic.response import redirect
from sanic_ext import Extend
from jinja2 import Environment, FileSystemLoader
from config import DB_CONFIG

# Crear la aplicación Sanic
app = Sanic("IncidenciasApp")
Extend(app)

# Configuración de la base de datos
app.config.update(DB_CONFIG)

# Configuración de Jinja2 (plantillas HTML)
env = Environment(loader=FileSystemLoader("templates"))

# Servir archivos estáticos (CSS, imágenes, etc.)
app.static("/static", "./static")


# ------------------- RUTAS -------------------

# Ruta raíz: redirige al login
@app.get("/")
async def home(request):
    return redirect("/login")


# Ruta GET para mostrar el formulario de login
@app.get("/login")
async def login_view(request):
    template = env.get_template("login.html")
    return response.html(template.render())


# Ruta POST para procesar el login
@app.post("/login")
async def login_post(request):
    from main import validar_usuario
    form = request.form
    usuario = form.get("usuario")
    password = form.get("password")

    user = await validar_usuario(usuario, password)
    if user:
        return redirect("/incidencias")
    else:
        template = env.get_template("error.html")
        return response.html(template.render(mensaje="Usuario o contraseña incorrectos"))


# Ruta GET para mostrar las incidencias
@app.get("/incidencias")
async def incidencias_view(request):
    from main import get_incidencias
    incidencias = await get_incidencias()
    template = env.get_template("incidencias.html")
    return response.html(template.render(incidencias=incidencias))


# Ruta POST para insertar una nueva incidencia
@app.post("/insert")
async def insert_incidencia_view(request):
    from main import insert_incidencia
    form = request.form
    usuario = form.get("usuario")
    descripcion = form.get("descripcion")

    if usuario and descripcion:
        await insert_incidencia(usuario, descripcion)

    return redirect("/incidencias")


# Ruta POST para eliminar una incidencia por ID
@app.post("/delete/<id:int>")
async def delete_incidencia_view(request, id):
    from main import delete_incidencia
    await delete_incidencia(id)
    return redirect("/incidencias")


# ------------------- EJECUCIÓN -------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)