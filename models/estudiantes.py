from sqlalchemy import (
    Table, Column, Integer, String, INT,
    Enum, DateTime, ForeignKey
)
from config.db import meta_data, engine

meta_data.clear()

estudiantes = Table(
    "estudiantes",
    meta_data,
    Column("id", Integer, primary_key=True, autoincrement=True),  
    Column("semestre_actual", INT, nullable=False),
    Column("estado_academico",
        Enum("activo", "suspendido","retirado","graduado", name="estado_academico"),
        default="activo"
    ),
    Column("id_usuarios", INT, ForeignKey("usuarios.id"), nullable=False),
    Column("id_programa", INT, ForeignKey("programas.id"), nullable=False),
    extend_existing=True
)


meta_data.create_all(engine)