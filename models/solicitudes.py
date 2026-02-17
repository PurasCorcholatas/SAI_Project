from sqlalchemy import Table, Column, Integer, String, ForeignKey, Enum,func, DateTime
from config.db import meta_data

meta_data.clear()

solicitudes = Table(
    "solicitudes",
    meta_data,
    Column("id", Integer, primary_key=True),
    Column("id_usuario", Integer, ForeignKey("usuarios.id")),
    Column("tipo", String(255,),nullable= False ),
    Column("descripcion", String(255)),
    Column(
        "estado",
        Enum("pendiente", "aprobado","rechazada", name="estado_solicitud"),
        default="activo"
    ),
    Column("creado_en",DateTime,
            server_default=func.now(),
            nullable=False
    ),
    extend_existing=True
)
