from sqlalchemy import select
from config.db import engine
from models.roles import roles

def obtener_roles():
    with engine.connect() as conn:
        return conn.execute(select(roles)).fetchall()
