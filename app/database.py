import asyncio
import aiomysql

from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME


async def crear_pool(app):
    intentos = 10

    for intento in range(1, intentos + 1):
        try:
            print(f"Intentando conectar a MySQL... intento {intento}")

            app.ctx.db = await aiomysql.create_pool(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                db=DB_NAME,
                autocommit=True,
                charset="utf8mb4"
            )

            print("Conexion a MySQL creada correctamente")
            return

        except Exception as error:
            print("MySQL no esta listo todavia:", error)
            await asyncio.sleep(3)

    raise Exception("No se pudo conectar a MySQL despues de varios intentos")


async def cerrar_pool(app):
    if hasattr(app.ctx, "db"):
        app.ctx.db.close()
        await app.ctx.db.wait_closed()


async def fetch_all(app, query, params=None):
    async with app.ctx.db.acquire() as conexion:
        async with conexion.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(query, params or ())
            return await cursor.fetchall()


async def fetch_one(app, query, params=None):
    async with app.ctx.db.acquire() as conexion:
        async with conexion.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(query, params or ())
            return await cursor.fetchone()


async def execute_query(app, query, params=None):
    async with app.ctx.db.acquire() as conexion:
        async with conexion.cursor() as cursor:
            await cursor.execute(query, params or ())
            return cursor.lastrowid