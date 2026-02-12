from sqlalchemy import Table, Column, Integer, String, ForeignKey, Enum
from config.db import meta_data

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
    extend_existing=True
)
