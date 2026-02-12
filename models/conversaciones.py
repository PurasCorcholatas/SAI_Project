from sqlalchemy import (
    Table, Column, Integer, String,
    Enum, DateTime, ForeignKey
)
from config.db import meta_data, engine

cursos = Table(
    "cursos",
    meta_data,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("nombre", String(100), nullable=False),
    Column("id_usuario", String(100),ForeignKey("usuario.id"), nullable=False),
    extend_existing=True
)

meta_data.create_all(engine)
