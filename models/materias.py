from sqlalchemy import (
    Table, Column, Integer, String,
    Enum, DateTime, ForeignKey
)
from config.db import meta_data, engine

meta_data.clear()

materias = Table(
    "materias",
    meta_data,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("codigo", String(100), nullable=False),
    Column("nombre", String(120), nullable=False, unique=True),
    Column("creditos", String(255), nullable=False),
    Column("id_programa", Integer, ForeignKey("programa.id"), nullable=False),
    
    
   
)

meta_data.create_all(engine)
