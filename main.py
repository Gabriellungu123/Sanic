# main.py
import aiomysql
from config import DB_CONFIG

async def connect_db():
    return await aiomysql.connect(
        host=DB_CONFIG['DB_HOST'],
        port=DB_CONFIG['DB_PORT'],
        user=DB_CONFIG['DB_USER'],
        password=DB_CONFIG['DB_PASSWORD'],
        db=DB_CONFIG['DB_NAME']
    )

async def get_incidencias():
    conn = await connect_db()
    async with conn.cursor(aiomysql.DictCursor) as cur:
        await cur.execute("SELECT * FROM usuarios")
        rows = await cur.fetchall()
    conn.close()
    return rows

async def insert_incidencia(usuario, descripcion):
    conn = await connect_db()
    async with conn.cursor() as cur:
        await cur.execute("INSERT INTO usuarios (usuario, descripcion) VALUES (%s, %s)", (usuario, descripcion))
        await conn.commit()
    conn.close()

async def delete_incidencia(id):
    conn = await connect_db()
    async with conn.cursor() as cur:
        await cur.execute("DELETE FROM usuarios WHERE id=%s", (id,))
        await conn.commit()
    conn.close()