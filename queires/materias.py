from sqlalchemy import select
from config.db import engine
from models.materias import materias

def obtener_materias():
    with engine.connect() as conn:
        return conn.execute(
            select(materias)
        ).fetchall()
