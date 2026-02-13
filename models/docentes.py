from sqlalchemy import (
    Table, Column, Integer, String,
    Enum, DateTime, ForeignKey
)
from config.db import meta_data, engine

docentes = Table(
    "docentes",
    meta_data,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("id_usuario", String(100), nullable=False),
    Column("especialidad", String(120), nullable=False, unique=True),
    Column("tipo_contrato", String(255), nullable=False),
    Column(
        "estado",
        Enum("activo", "inactivo", name="estado_docente"),
        default="activo"
    ),
    extend_existing=True
   
)

meta_data.create_all(engine)
