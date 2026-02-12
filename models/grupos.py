from sqlalchemy import (
    Table, Column, Integer, String, INT,
    Enum, DateTime, ForeignKey
)
from config.db import meta_data, engine

grupos = Table(
    "grupos",
    meta_data,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("id_materia", INT,ForeignKey("materia.id"), nullable=False),
    Column("id_docente", INT, ForeignKey("docente.id"),  nullable=False),
    Column("id_periodo", INT,ForeignKey("periodos.id"), nullable=False),
    Column("cupo", INT, nullable=False),
    Column("horario", String(200), nullable=False),
    extend_existing=True
   
)

meta_data.create_all(engine)
