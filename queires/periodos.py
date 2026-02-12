from sqlalchemy import select
from config.db import engine
from models.periodos import periodos

def obtener_periodos():
    with engine.connect() as conn:
        return conn.execute(select(periodos)).fetchall()
