from sqlalchemy import select
from config.db import engine
from models.logs_interacciones import logs_interacciones

def obtener_logs_interacciones():
    with engine.connect() as conn:
        return conn.execute(select(logs_interacciones)).fetchall()
