from sqlalchemy import (
    Table, Column, Integer, String,
    Enum, DateTime, ForeignKey
)
from config.db import meta_data, engine

meta_data.clear()

cursos = Table(
    "cursos",
    meta_data,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("nombre", String(100), nullable=False),
    Column("descripcion", String(120), nullable=False, unique=True),
    Column("programa_id", String(100),ForeignKey("programa.id"), nullable=False),
    extend_existing=True
)

meta_data.create_all(engine)
