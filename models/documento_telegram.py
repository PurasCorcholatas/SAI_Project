from sqlalchemy import Table, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from config.db import engine, meta_data

meta_data.clear()

documentos_telegram = Table(
    "documentos_telegram",
    meta_data,
    Column("id", Integer, primary_key=True),
    Column("id_usuario", Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False),
    Column("nombre_original", String(255), nullable=False),
    Column("ruta_archivo", String(500), nullable=False),
    Column("mime_type", String(50), nullable=True),
    Column("fecha_subida", DateTime, nullable=False, server_default=func.now()),
    extend_existing=True
)

meta_data.create_all(engine)
