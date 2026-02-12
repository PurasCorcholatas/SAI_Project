from sqlalchemy import select
from models.faq import faq
from config.db import engine

def get_faq_data():
    with engine.connect() as conn:
        result = conn.execute(
            select(
                faq.c.pregunta,
                faq.c.respuesta
            )
        )
        return result.fetchall()




def obtener_cursos():
    return []

def obtener_docentes():
    return []


def obtener_estudiantes():
    return []

def obtener_faq():
    return []


def obtener_grupos():
    return []

def obtener_logs_interacciones():
    return []

def obtener_materias():
    return []

def obtener_matriculas():
    return []


def obtener_notas():
    return []

def obtener_periodos():
    return []

def obtener_programas():
    return []

def obtener_roles():
    return []

def obtener_solicitudes():
    return []

def obtener_usuarios():
    return []
