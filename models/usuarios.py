from sqlalchemy import (
    Table, Column, Integer, String,
    Enum, DateTime, ForeignKey, func
)
from config.db import meta_data, engine

usuarios = Table(
    "usuarios",
    meta_data,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("nombre", String(100), nullable=False),
    Column("email", String(120), nullable=False, unique=True),
    Column("password_hash", String(255), nullable=False),
    Column("id_rol", Integer, ForeignKey("roles.id"), nullable=False),
    Column(
        "estado",
        Enum("activo", "inactivo", name="estado_usuario"),
        default="activo"
    ),
    Column(
        "creado_en",
        DateTime,
            server_default=func.now(),
            nullable=False
    ),
    extend_existing=True
)

meta_data.create_all(engine)
