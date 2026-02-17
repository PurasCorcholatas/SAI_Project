from langchain.tools import tool
from sqlalchemy import text
from config.db import engine

@tool
def registrar_matricula(id_usuario: int, id_grupo: int) -> str:
    """
    Registra una matrícula en la base de datos.
    """

    try:
        with engine.begin() as conn:

            estudiante = conn.execute(
                text("SELECT id FROM estudiantes WHERE id_usuario = :uid"),
                {"uid": id_usuario}
            ).fetchone()

            if not estudiante:
                return f"No se encontró un estudiante con id_usuario {id_usuario}"

            id_estudiante = estudiante[0]

            grupo = conn.execute(
                text("SELECT id FROM grupos WHERE id = :gid"),
                {"gid": id_grupo}
            ).fetchone()

            if not grupo:
                return f"No existe un grupo con id {id_grupo}"

            existe = conn.execute(
                text("""
                    SELECT id FROM matriculas
                    WHERE id_estudiante = :id_est
                    AND id_grupo = :id_grupo
                """),
                {
                    "id_est": id_estudiante,
                    "id_grupo": id_grupo
                }
            ).fetchone()

            if existe:
                return "El estudiante ya está matriculado en este grupo."

            conn.execute(
                text("""
                    INSERT INTO matriculas (id_estudiante, id_grupo)
                    VALUES (:id_est, :id_grupo)
                """),
                {
                    "id_est": id_estudiante,
                    "id_grupo": id_grupo
                }
            )

        return "Matrícula registrada exitosamente."

    except Exception as e:
        print("ERROR REAL:", e)
        return f"Ocurrió un error al registrar la matrícula: {str(e)}"
