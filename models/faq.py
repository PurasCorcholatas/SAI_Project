from sqlalchemy import Table, Column
from sqlalchemy.sql.sqltypes import Integer, String , DateTime
from config.db import engine, meta_data


faq = Table("faq", meta_data,
            Column("id", Integer, primary_key=True),
            Column("pregunta", String(200), nullable=False),
            Column("respuesta", String(200), nullable=False),
            Column("categoria", String(200), nullable=False),
            Column("creado_en", DateTime, nullable=False),
            Column("actualizado_en", DateTime, nullable=False),
            extend_existing=True
            )
            

meta_data.create_all(engine)