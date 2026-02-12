
from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select

from fastapi import APIRouter

from pydantic import BaseModel
from langchain_core.messages import AIMessage
from graph.graph import graph  


from config.db import engine, get_db
from schema.faq_schema import Faq_Schema
from models.faq import faq
from models.usuarios import usuarios
from services.embedding_service import buscar_faq
from services.chat_service import procesar_mensaje
from graph.service import chat_sai



user = APIRouter()
chat = APIRouter()
test_usuarios = APIRouter()



@user.get("/")
def root():
    return {"status": "ok"}


@user.post("/api/faq")
def create_faq(data_faq: Faq_Schema):
    with engine.begin() as conn:
        conn.execute(faq.insert().values(data_faq.dict()))
    return {"success": True}


@user.get("/api/faq/buscar")
def faq_usuario(texto: str = Query(...)):
    respuesta = buscar_faq(texto)
    return {"usuario": texto, "respuesta": respuesta}


chat = APIRouter()
user = APIRouter()


class ChatRequest(BaseModel):
    message: str
    session_id: str


class ChatResponse(BaseModel):
    answer: str


def serialize_messages(messages):
    serialized = []
    for m in messages:
        if isinstance(m, AIMessage):
            serialized.append({"role": "ai", "content": m.content})
        elif isinstance(m, dict):
            serialized.append(m)
        else:
            serialized.append({"content": str(m)})
    return serialized






def route_chat(state):
    text = state["messages"][-1].content.lower()

    faq_keywords = [
        "registro", "inscripción", "horario",
        "nota", "materia", "docente", "semestre"
    ]

    if any(k in text for k in faq_keywords):
        return "rag"

    return "chat"



@test_usuarios.get("/test/usuarios")
def get_test_usuarios(db: Session = Depends(get_db)):
    stmt = select(usuarios)
    result = db.execute(stmt).fetchall()

    return {
        "total": len(result),
        "usuarios": [dict(row._mapping) for row in result]
    }


@chat.post("/chat", response_model=ChatResponse)
def chat_endpoint(payload: ChatRequest, db: Session = Depends(get_db)):

    state = {
        "messages": [{"role": "user", "content": payload.message}],
        "intent": "general",
        "context": "",
    }

    result = graph.invoke(
    state,
    config={
        "configurable": {
            "thread_id": payload.session_id
        }
        }
    )


    messages = result.get("messages", [])
    answer = messages[-1].content if messages else "No se pudo generar respuesta."

    return {"answer": answer}


