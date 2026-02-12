from sqlalchemy import select
from config.db import engine
from models.notas import notas

def obtener_notas():
    with engine.connect() as conn:
        return conn.execute(select(notas)).fetchall()
