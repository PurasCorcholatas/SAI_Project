from sqlalchemy.orm import Session
from sqlalchemy import select
from models.usuarios import usuarios
from models.docentes import docentes
from models.faq import faq
from models.grupos import grupos
from models.logs_interacciones import logs_interacciones
from models.materias import materias
from models.estudiantes import estudiantes
from models.matricula import matriculas

from models.notas import notas
from models.periodos import periodos
from models.programas import programas
from models.roles import roles
from models.solicitudes import solicitudes
from models.cursos import cursos



def obtener_usuarios(db: Session):
    result = db.execute(select(usuarios)).fetchall()
    return [dict(r._mapping) for r in result]


def obtener_docentes(db: Session):
    result = db.execute(select(docentes)).fetchall()
    return [dict(r._mapping) for r in result]

def obtener_faq(db: Session):
    result = db.execute(select(faq)).fetchall()
    return [dict(r._mapping) for r in result]

def obtener_grupos(db: Session):
    result = db.execute(select(grupos)).fetchall()
    return [dict(r._mapping) for r in result]

def obtener_logs_interacciones(db: Session):
    result = db.execute(select(logs_interacciones)).fetchall()
    return [dict(r._mapping) for r in result]

def obtener_materias(db: Session):
    result = db.execute(select(materias)).fetchall()
    return [dict(r._mapping) for r in result]

def obtener_matriculas(db: Session):
    result = db.execute(select(matriculas)).fetchall()
    return [dict(r._mapping) for r in result]

def obtener_notas(db: Session):
    result = db.execute(select(notas)).fetchall()
    return [dict(r._mapping) for r in result]

def obtener_periodos(db: Session):
    result = db.execute(select(periodos)).fetchall()
    return [dict(r._mapping) for r in result]

def obtener_programas(db: Session):
    result = db.execute(select(programas)).fetchall()
    return [dict(r._mapping) for r in result]

def obtener_roles(db: Session):
    result = db.execute(select(roles)).fetchall()
    return [dict(r._mapping) for r in result]

def obtener_solicitudes(db: Session):
    result = db.execute(select(solicitudes)).fetchall()
    return [dict(r._mapping) for r in result]

def obtener_estudiantes(db: Session):
    result = db.execute(select(estudiantes)).fetchall()
    return [dict(r._mapping) for r in result]

def obtener_cursos(db: Session):
    result = db.execute(select(cursos)).fetchall()
    return [dict(r._mapping) for r in result]
