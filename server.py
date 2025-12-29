# server.py
from sanic import Sanic, response
from sanic.response import redirect
from sanic_ext import Extend
from jinja2 import Environment, FileSystemLoader
from config import DB_CONFIG

app = Sanic("IncidenciasApp")
Extend(app)

# Configuración estilo Sanic
app.config.update(DB_CONFIG)

# Jinja2
env = Environment(loader=FileSystemLoader("templates"))
app.static("/static", "./static")
@app.get("/")
async def home(request):
    return redirect("/login")

@app.get("/login")
async def login_view(request):
    template = env.get_template("login.html")
    return response.html(template.render())

@app.get("/incidencias")
async def incidencias_view(request):
    from main import get_incidencias
    incidencias = await get_incidencias()
    template = env.get_template("incidencias.html")
    return response.html(template.render(incidencias=incidencias))

@app.post("/insert")
async def insert_incidencia_view(request):
    from main import insert_incidencia
    form = request.form
    usuario = form.get("usuario")
    descripcion = form.get("descripcion")

    if usuario and descripcion:
        await insert_incidencia(usuario, descripcion)

    return response.redirect("/incidencias")


@app.post("/delete/<id:int>")
async def delete_incidencia_view(request, id):
    from main import delete_incidencia
    await delete_incidencia(id)
    return response.redirect("/incidencias")








if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)