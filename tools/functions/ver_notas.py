from langchain.tools import tool
from sqlalchemy import text
from config.db import engine

@tool
def ver_notas(id_usuario: int) -> str:
    """
    Muestra las notas de un estudiante.
    """

    try:
        with engine.begin() as conn:

            
            usuario = conn.execute(
                text("""
                    SELECT u.id, r.nombre
                    FROM usuarios u
                    JOIN roles r ON u.id_rol = r.id
                    WHERE u.id = :uid
                """),
                {"uid": id_usuario}
            ).fetchone()

            if not usuario:
                return "El usuario no existe."

            if usuario[1].lower() != "estudiante":
                return "Solo los estudiantes pueden consultar notas."

            
            notas = conn.execute(
                text("""
                    SELECT 
                        m.nombre AS materia,
                        n.tipo_evaluacion,
                        n.nota
                    FROM notas n
                    JOIN matriculas ma ON n.id_matricula = ma.id
                    JOIN grupos g ON ma.id_grupo = g.id
                    JOIN materias m ON g.id_materia = m.id
                    JOIN estudiantes e ON ma.id_estudiante = e.id
                    WHERE e.id_usuario = :uid
                """),
                {"uid": id_usuario}
            ).fetchall()

            if not notas:
                return "No hay notas registradas."

            resultado = "Notas del estudiante:\n\n"

            for materia, tipo, nota in notas:
                resultado += f"{materia} - {tipo}: {nota}\n"

            return resultado

    except Exception as e:
        print("ERROR REAL:", e)
        return f"Ocurrió un error al consultar las notas: {str(e)}"
