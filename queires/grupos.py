from sqlalchemy import select
from config.db import engine
from models.grupos import grupos

def obtener_grupos():
    with engine.connect() as conn:
        return conn.execute(select(grupos)).fetchall()
