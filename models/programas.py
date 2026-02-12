from sqlalchemy import (
    Table, Column, Integer, String, INT,
    Enum, DateTime, ForeignKey
)
from config.db import meta_data, engine

programas = Table(
    "programas",
    meta_data,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("nombre", String(100), nullable=False),
    Column("facultas", String(120), nullable=False, unique=True),
    Column("duracion_semestres", INT, nullable=False),
    Column(
        "estado",
        Enum("activo", "inactivo", name="estado_programas"),
        default="activo"
    ),
    extend_existing=True
)

meta_data.create_all(engine)
