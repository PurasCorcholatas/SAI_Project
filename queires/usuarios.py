from sqlalchemy import select
from config.db import engine
from models.usuarios import usuarios

def obtener_usuarios():
    with engine.connect() as conn:
        return conn.execute(select(usuarios)).fetchall()

def obtener_usuarios_activos():
    with engine.connect() as conn:
        return conn.execute(
            select(usuarios).where(usuarios.c.activo == True)
        ).fetchall()
