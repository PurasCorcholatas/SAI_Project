from sqlalchemy import (
    Table, Column, Integer, String, INT,
    Enum, DateTime, ForeignKey
)
from sqlalchemy.types import DECIMAL
from config.db import meta_data, engine

meta_data.clear()

notas = Table(
    "notas",
    meta_data,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("id_matricula", INT,ForeignKey("matriculas.id"), nullable=False),
    Column("tipo_evaluacion", String(200), nullable=False),
    Column("nota", DECIMAL(2,3), nullable=False),
    extend_existing=True
    
)

meta_data.create_all(engine)
