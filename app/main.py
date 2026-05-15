from pathlib import Path

from sanic import Sanic
from jinja2 import Environment, FileSystemLoader

from database import crear_pool, cerrar_pool
from routes.auth import auth_bp
from routes.incidencias import incidencias_bp
from routes.grupos import grupos_bp
from routes.usuarios import usuarios_bp


BASE_DIR = Path(__file__).resolve().parent

app = Sanic("IncidenciasApp")

app.static("/static", BASE_DIR / "static")

templates = Environment(
    loader=FileSystemLoader(BASE_DIR / "templates"),
    autoescape=True
)

app.ctx.templates = templates

app.blueprint(auth_bp)
app.blueprint(incidencias_bp)
app.blueprint(grupos_bp)
app.blueprint(usuarios_bp)


@app.listener("before_server_start")
async def iniciar_base_datos(app):
    print("Conectando a MySQL...")
    await crear_pool(app)
    print("Conexion a MySQL creada correctamente")


@app.listener("after_server_stop")
async def cerrar_base_datos(app):
    print("Cerrando conexion MySQL...")
    await cerrar_pool(app)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8000,
        debug=True,
        single_process=True
    )