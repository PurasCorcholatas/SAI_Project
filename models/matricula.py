from sqlalchemy import (
    Table, Column, Integer, String, INT,
    Enum, DateTime, ForeignKey
)
from config.db import meta_data, engine

matriculas = Table(
    "matriculas",
    meta_data,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("id_estudiante", INT,ForeignKey("estudiante.id"), nullable=False),
    Column("id_grupo", INT,ForeignKey("grupo.id"), nullable=False),
    Column("fecha_matricula", DateTime,
    server_default="CURRENT_TIMESTAMP", 
    nullable=False),
    Column("duracion_semestres", INT, nullable=False),
    Column(
        "estado",
        Enum("activo", "inactivo","finalizada", name="estado_matriculas"),
        default="activo"
    ),
    extend_existing=True
)

meta_data.create_all(engine)
