from sqlalchemy import (
    Table, Column, Integer, String, INT,Text,

    Enum, DateTime, ForeignKey
)
from config.db import meta_data, engine

logs_interacciones = Table(
    "logs_interacciones",
    meta_data,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("id_usuario", INT,ForeignKey("usuario.id"),  nullable=False),
    Column("mensaje", Text, nullable=False),
    Column("respuesta", Text, nullable=False),
    Column("creado_en", DateTime,
    server_default="CURRENT_TIMESTAMP", 
    nullable=False),
    extend_existing=True
    
)

meta_data.create_all(engine)
