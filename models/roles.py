from sqlalchemy import Table, Column, func
from sqlalchemy.sql.sqltypes import Integer, String , DateTime
from config.db import engine, meta_data


roles = Table(
    "roles", meta_data,
            Column("id", Integer, primary_key=True),
            Column("nombre", String(200), nullable=False),
            Column("descripcion", String(200), nullable=False),
            Column("creado_en",DateTime,
            server_default=func.now(),
            nullable=False
            ),
            extend_existing=True
            )
            

meta_data.create_all(engine)