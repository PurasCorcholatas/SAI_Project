from sqlalchemy import select
from config.db import engine
from models.faq import faq

def obtener_faq():
    with engine.connect() as conn:
        return conn.execute(select(faq)).fetchall()
