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


# Ruta GET para mostrar las incidencias (con usuarios disponibles para asignar)
@app.get("/incidencias")
async def incidencias_view(request):
    from main import get_incidencias, get_usuarios
    incidencias = await get_incidencias()
    usuarios = await get_usuarios()
    template = env.get_template("incidencias.html")
    return response.html(template.render(incidencias=incidencias, usuarios=usuarios))


# Ruta POST para insertar una nueva incidencia (con todos los campos)
@app.post("/insert")
async def insert_incidencia_view(request):
    from main import insert_incidencia
    form = request.form

    resumen = form.get("resumen")
    servicio = form.get("servicio")
    prioridad = form.get("prioridad")
    estado = form.get("estado")
    usuario = form.get("usuario")
    fecha_deseada = form.get("fecha_deseada")

    if resumen and servicio and prioridad and estado and usuario and fecha_deseada:
        await insert_incidencia(resumen, servicio, prioridad, estado, usuario, fecha_deseada)

    return redirect("/incidencias")


# Ruta POST para eliminar una incidencia por ID
@app.post("/delete/<id>")
async def delete_incidencia_view(request, id):
    from main import delete_incidencia
    await delete_incidencia(id)
    return redirect("/incidencias")


# Ruta GET para editar incidencia
@app.get("/editar/<id>")
async def editar_incidencia_view(request, id):
    from main import get_incidencia_por_id
    incidencia = await get_incidencia_por_id(id)

    template = env.get_template("editar.html")
    return response.html(template.render(incidencia=incidencia))


# Ruta POST para guardar edición de incidencia
@app.post("/editar/<id>")
async def editar_incidencia_post(request, id):
    from main import update_incidencia
    form = request.form

    resumen = form.get("resumen")
    servicio = form.get("servicio")
    prioridad = form.get("prioridad")
    estado = form.get("estado")
    fecha_deseada = form.get("fecha_deseada")

    await update_incidencia(id, resumen=resumen, servicio=servicio,
                            prioridad=prioridad, estado=estado, fecha_deseada=fecha_deseada)

    return redirect("/incidencias")


# Ruta GET para ver detalles de una incidencia
@app.get("/incidencia/<id>")
async def incidencia_detalle_view(request, id):
    from main import get_incidencia_por_id
    incidencia = await get_incidencia_por_id(id)

    template = env.get_template("detalle_incidencia.html")
    return response.html(template.render(incidencia=incidencia))

# Ruta GET para mostrar el formulario de creación
@app.get("/crear")
async def crear_incidencia_view(request):
    from main import get_usuarios
    usuarios = await get_usuarios()
    template = env.get_template("crear_incidencia.html")
    return response.html(template.render(usuarios=usuarios))


# ------------------- EJECUCIÓN -------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)