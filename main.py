from sanic import Sanic
from sanic.response import text
from sanic_ext import Extend, render

app = Sanic("MyHelloWorldApp")

# ACTIVAR SANIC-EXT
Extend(app)

# Servir estáticos
app.static("/static", "./static")

@app.get("/")
async def index(request):
    return await render("login.html")

@app.post("/login")
async def login(request):
    username = request.form.get("username")
    password = request.form.get("password")
    return text(f"Usuario: {username}, Contraseña: {password}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)