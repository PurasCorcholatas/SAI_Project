from sqlalchemy import (
    Table, Column, Integer, String, INT,
    Enum, DateTime, ForeignKey, func
)
from config.db import meta_data, engine

meta_data.clear()

matriculas = Table(
    "matriculas",
    meta_data,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("id_estudiante", INT,ForeignKey("estudiantes.id"), nullable=False),
    Column("id_grupo", INT,ForeignKey("grupos.id"), nullable=False),
    Column(
        "estado",
        Enum("activo", "inactivo","finalizada", name="estado_matriculas"),
        default="activo",nullable=False
    ),
    extend_existing=True
)

meta_data.create_all(engine)
