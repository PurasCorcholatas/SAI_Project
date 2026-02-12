from sqlalchemy import select
from config.db import engine
from models.solicitudes import solicitudes

def obtener_solicitudes():
    with engine.connect() as conn:
        return conn.execute(
            select(solicitudes)
        ).fetchall()
