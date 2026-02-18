from langchain.tools import tool
from sqlalchemy import text
from config.db import engine

@tool
def registrar_matricula(id_estudiante: int, id_grupo: int) -> str:
    """
    Registra una matrícula o cambia de grupo si ya existe.
    """

    try:
        with engine.begin() as conn:

            
            estudiante = conn.execute(
                text("SELECT id FROM estudiantes WHERE id = :eid"),
                {"eid": id_estudiante}
            ).fetchone()

            if not estudiante:
                return f"No se encontró un estudiante con id {id_estudiante}"

            id_estudiante = estudiante[0]

            grupo = conn.execute(
                text("SELECT id FROM grupos WHERE id = :gid"),
                {"gid": id_grupo}
            ).fetchone()

            if not grupo:
                return f"No existe un grupo con id {id_grupo}"

            
            matricula_actual = conn.execute(
                text("""
                    SELECT id, id_grupo FROM matriculas
                    WHERE id_estudiante = :id_est
                """),
                {"id_est": id_estudiante}
            ).fetchone()

            if matricula_actual:

               
                if matricula_actual[1] == id_grupo:
                    return "El estudiante ya está en ese grupo."

                
                conn.execute(
                    text("""
                        UPDATE matriculas
                        SET id_grupo = :id_grupo
                        WHERE id_estudiante = :id_est
                    """),
                    {
                        "id_est": id_estudiante,
                        "id_grupo": id_grupo
                    }
                )

                return "Grupo actualizado correctamente."

            
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
