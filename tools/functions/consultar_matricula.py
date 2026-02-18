from sqlalchemy import text
from config.db import engine
from langchain.tools import tool

@tool
def consultar_matricula(nombre: str = None, email: str = None):
    """
    Consulta la matrícula de un estudiante por nombre o email.
    """
    print("Entró a la tool")
    with engine.connect() as conn:
        query = """
            SELECT 
                u.nombre,
                u.email,
                e.semestre_actual,
                e.estado_academico
            FROM estudiantes e
            JOIN usuarios u ON e.id_usuario = u.id
            WHERE 1=1
        """
        params = {}
        if nombre:
            query += " AND u.nombre = :nombre"
            params["nombre"] = nombre
        if email:
            query += " AND u.email = :email"
            params["email"] = email
        
        estudiante = conn.execute(text(query), params).fetchone()

    if not estudiante:
        return "No se encontró matrícula para el estudiante."

    return f"""
    Estudiante: {estudiante.nombre}
    Email: {estudiante.email}
    Semestre: {estudiante.semestre_actual}
    Estado: {estudiante.estado_academico}
    """
