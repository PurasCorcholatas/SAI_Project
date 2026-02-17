from sqlalchemy import (
    Table, Column, Integer, String, INT,
    Enum, DateTime, ForeignKey
)
from config.db import meta_data, engine

grupos = Table(
    "grupos",
    meta_data,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("cupo", INT, nullable=False),
    Column("horario", String(100), nullable=False),
    Column("aula", String(100), nullable=False),
    Column("id_docente", INT, ForeignKey("docente.id"),  nullable=False),
    Column("id_periodo", INT,ForeignKey("periodos.id"), nullable=False),

    extend_existing=True
   
)

meta_data.create_all(engine)
