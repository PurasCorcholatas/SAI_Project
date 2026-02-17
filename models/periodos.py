from sqlalchemy import (
    Table, Column, Integer, String, DATE, 
    Enum, DateTime, ForeignKey
)
from config.db import meta_data, engine

meta_data.clear()

periodos = Table(
    "periodos",
    meta_data,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("nombre", String(100), nullable=False),
    Column("fecha_inicio", DATE, nullable=False, unique=True),
    Column("fecha_fin", DATE, nullable=False),
    Column(
        "estado",
        Enum("activo", "cerrado", name="estado_periodo"),
        default="activo"
    ),
    extend_existing=True
)

meta_data.create_all(engine)
