from langchain.tools import tool
from sqlalchemy import text
from config.db import engine

@tool
def buscar_correo(nombre: str) -> str:
    """
    Busca el correo electrónico de un usuario por nombre.
    """

    with engine.begin() as conn:
        correo = conn.execute(
            text("SELECT email FROM usuarios WHERE nombre=:nom"),
            {"nom": nombre}
        ).fetchone()

    if correo:
        return f"Tu correo registrado es: {correo[0]}"
    else:
        return "No encontré un correo con ese nombre."
