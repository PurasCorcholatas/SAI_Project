from sqlalchemy import (
    Table, Column, Integer, String,
    Enum, DateTime, ForeignKey, INT
)
from config.db import meta_data, engine

meta_data.clear()


docentes = Table(
    "docentes",
    meta_data,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("especialidad", String(120), nullable=False, unique=True),
    Column(
        "tipo_contrato",
        Enum("tiempo_completo", "medio_tiempo","parcial", name="estado_docente"),
        default="activo"
    ),
    Column(
        "estado",
        Enum("activo", "inactivo", name="estado_docente"),
        default="activo"
    ),
    Column("id_usuario", INT,ForeignKey("usuarios.id"), nullable=False),
    extend_existing=True
   
)

meta_data.create_all(engine)
