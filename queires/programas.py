from sqlalchemy import select
from config.db import engine
from models.programas import programas

def obtener_programas():
    with engine.connect() as conn:
        return conn.execute(select(programas)).fetchall()
