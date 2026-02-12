from sqlalchemy import select, join
from models.docentes import docentes
from models.usuarios import usuarios

def obtener_docentes(conn):  
    j = join(docentes, usuarios, docentes.c.id_usuario == usuarios.c.id)

    stmt = (
        select(usuarios.c.nombre)
        .select_from(j)
        .where(docentes.c.estado == "activo")
    )

    result = conn.execute(stmt).fetchall()

    return [row[0] for row in result]
