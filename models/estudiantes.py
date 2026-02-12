from sqlalchemy import (
    Table, Column, Integer, String, INT,
    Enum, DateTime, ForeignKey
)
from config.db import meta_data, engine

estudiantes = Table(
    "estudiantes",
    meta_data,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("id_usuario", INT, nullable=False),
    Column("codigo_estudiante", INT, nullable=False),
    Column("semestre_actual", INT, nullable=False),
    Column("id_usuarios", Integer,ForeignKey("usuarios.id"),  nullable=False),
    Column("id_programa", INT,ForeignKey("programas.id"), nullable=False),
    Column(
        "estado_academico",
        Enum("activo", "suspendido","retirado", name="estado_academico"),
        default="activo"
    ),
    extend_existing=True
   
)

meta_data.create_all(engine)
