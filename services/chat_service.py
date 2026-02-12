from services.embedding_service import buscar_en_embeddings
from services.db_service import (
    obtener_usuarios,
    obtener_cursos,
    obtener_docentes,
    obtener_estudiantes,
    obtener_faq,
    obtener_grupos,
    obtener_logs_interacciones,
    obtener_materias,
    obtener_matriculas,
    obtener_notas,
    obtener_periodos,
    obtener_programas,
    obtener_roles,
    obtener_solicitudes,
    
)
from config.db import get_db
from sqlalchemy.orm import Session

def procesar_mensaje(texto: str, db: Session):
    """
    Devuelve resultados: primero embeddings, luego fallback BD
    """
   
    resultados = buscar_en_embeddings(texto)
    if resultados:
        return resultados

    
    text_lower = texto.lower()
    if "docentes" in text_lower:
        return obtener_docentes(db)
    elif "curso" in text_lower:
        return obtener_cursos(db)
    elif "estudiantes" in text_lower:
        return obtener_estudiantes(db)
    elif "faq" in text_lower:
        return obtener_faq(db)
    elif "grupos" in text_lower:
        return obtener_grupos(db)
    elif "logs_interacciones" in text_lower:
        return obtener_logs_interacciones(db)
    elif "materias" in text_lower:
        return obtener_materias(db)
    elif "matriculas" in text_lower:
        return obtener_matriculas(db)
    elif "notas" in text_lower:
        return obtener_notas(db)
    elif "periodos" in text_lower:
        return obtener_periodos(db)
    elif "programas" in text_lower:
        return obtener_programas(db)
    elif "roles" in text_lower:
        return obtener_roles(db)
    elif "solicitudes" in text_lower:
        return obtener_solicitudes(db)
    elif "usuarios" in text_lower:
        return obtener_usuarios(db)
   
    
    else:
        return []
