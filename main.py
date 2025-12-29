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
        await cur.execute("""
            SELECT i.id, u.usuario, i.descripcion
            FROM incidencias i
            JOIN usuarios u ON i.usuario_id = u.id
        """)
        rows = await cur.fetchall()
    conn.close()
    return rows

async def insert_incidencia(usuario, descripcion):
    conn = await connect_db()
    async with conn.cursor() as cur:
        # Buscar el id del usuario
        await cur.execute("SELECT id FROM usuarios WHERE usuario=%s", (usuario,))
        result = await cur.fetchone()
        if result:
            usuario_id = result[0]
            await cur.execute("INSERT INTO incidencias (usuario_id, descripcion) VALUES (%s, %s)", (usuario_id, descripcion))
            await conn.commit()
    conn.close()

async def delete_incidencia(id):
    conn = await connect_db()
    async with conn.cursor() as cur:
        await cur.execute("DELETE FROM incidencias WHERE id=%s", (id,))
        await conn.commit()
    conn.close()

async def validar_usuario(usuario, password):
    conn = await connect_db()
    async with conn.cursor(aiomysql.DictCursor) as cur:
        await cur.execute("SELECT * FROM usuarios WHERE usuario=%s AND password=%s", (usuario, password))
        row = await cur.fetchone()
    conn.close()
    return row