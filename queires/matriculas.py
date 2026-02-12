from sqlalchemy import select
from config.db import engine
from models.matricula import matriculas

def obtener_matriculas():
    with engine.connect() as conn:
        return conn.execute(select(matriculas)).fetchall()
