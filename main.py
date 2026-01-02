import aiomysql
from config import DB_CONFIG
import random

# Generar ID de 8 dígitos
def generar_id():
    return str(random.randint(10000000, 99999999))


# ------------------- CONEXIÓN -------------------
async def connect_db():
    return await aiomysql.connect(
        host=DB_CONFIG['DB_HOST'],
        port=DB_CONFIG['DB_PORT'],
        user=DB_CONFIG['DB_USER'],
        password=DB_CONFIG['DB_PASSWORD'],
        db=DB_CONFIG['DB_NAME']
    )


# ------------------- CRUD INCIDENCIAS -------------------

# Insertar incidencia completa (con descripción y departamento)
async def insert_incidencia(resumen, descripcion, servicio, prioridad, estado, usuario, fecha_deseada, departamento):
    conn = await connect_db()
    try:
        async with conn.cursor() as cur:
            # Buscar el id del usuario en usuarios_general
            await cur.execute("SELECT id FROM usuarios_general WHERE usuario=%s", (usuario,))
            result = await cur.fetchone()
            if not result:
                return False  # Usuario no encontrado
            usuario_id = result[0]
            incidencia_id = generar_id()
            await cur.execute("""
                INSERT INTO incidencias (id, resumen, descripcion, servicio, prioridad, estado, usuario_id, fecha_deseada, departamento)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (incidencia_id, resumen, descripcion, servicio, prioridad, estado, usuario_id, fecha_deseada, departamento))
            await conn.commit()
            return True
    finally:
        conn.close()


# Obtener todas las incidencias
async def get_incidencias():
    conn = await connect_db()
    try:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("""
                SELECT i.id, i.resumen, i.descripcion, i.servicio, i.prioridad, i.estado, i.fecha_deseada,
                       i.departamento, u.usuario, u.nombre_completo
                FROM incidencias i
                JOIN usuarios_general u ON i.usuario_id = u.id
            """)
            return await cur.fetchall()
    finally:
        conn.close()


# Obtener incidencia por ID
async def get_incidencia_por_id(id):
    conn = await connect_db()
    try:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("""
                SELECT i.id, i.resumen, i.descripcion, i.servicio, i.prioridad, i.estado, i.fecha_deseada,
                       i.departamento, u.usuario, u.nombre_completo
                FROM incidencias i
                JOIN usuarios_general u ON i.usuario_id = u.id
                WHERE i.id = %s
            """, (id,))
            row = await cur.fetchone()
            return row
    finally:
        conn.close()


# Actualizar o eliminar incidencia según estado
async def update_or_delete_incidencia(id, resumen=None, descripcion=None, servicio=None, prioridad=None, estado=None, fecha_deseada=None, departamento=None):
    conn = await connect_db()
    try:
        async with conn.cursor() as cur:
            if estado == "Resuelto":
                await cur.execute("DELETE FROM incidencias WHERE id=%s", (id,))
                await conn.commit()
                return "deleted"
            else:
                campos, valores = [], []
                if resumen:
                    campos.append("resumen=%s"); valores.append(resumen)
                if descripcion:
                    campos.append("descripcion=%s"); valores.append(descripcion)
                if servicio:
                    campos.append("servicio=%s"); valores.append(servicio)
                if prioridad:
                    campos.append("prioridad=%s"); valores.append(prioridad)
                if estado:
                    campos.append("estado=%s"); valores.append(estado)
                if fecha_deseada:
                    campos.append("fecha_deseada=%s"); valores.append(fecha_deseada)
                if departamento:
                    campos.append("departamento=%s"); valores.append(departamento)

                if campos:
                    query = f"UPDATE incidencias SET {', '.join(campos)} WHERE id=%s"
                    valores.append(id)
                    await cur.execute(query, tuple(valores))
                    await conn.commit()
                    return "updated"
    finally:
        conn.close()


# ------------------- USUARIOS -------------------

# Validar login (usuarios de informática)
async def validar_usuario(usuario, password):
    conn = await connect_db()
    try:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM usuarios_informatica WHERE usuario=%s AND password=%s", (usuario, password))
            row = await cur.fetchone()
            return row
    finally:
        conn.close()


# Obtener lista de usuarios de informática
async def get_usuarios_informatica():
    conn = await connect_db()
    try:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT id, usuario FROM usuarios_informatica")
            rows = await cur.fetchall()
            return rows
    finally:
        conn.close()


# Obtener lista de usuarios generales
async def get_usuarios_general(departamento=None):
    conn = await connect_db()
    try:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            if departamento:
                await cur.execute("SELECT id, usuario, nombre_completo FROM usuarios_general WHERE departamento=%s", (departamento,))
            else:
                await cur.execute("SELECT id, usuario, nombre_completo, departamento FROM usuarios_general")
            rows = await cur.fetchall()
            return rows
    finally:
        conn.close()