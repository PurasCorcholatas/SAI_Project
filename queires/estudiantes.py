from sqlalchemy import select
from config.db import engine
from models.estudiantes import estudiantes

def obtener_estudiantes():
    with engine.connect() as conn:
        return conn.execute(select(estudiantes)).fetchall()
