from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from pydantic import BaseModel
from langchain_core.messages import AIMessage
from graph.graph import graph  

from config.db import engine, get_db
from schema.faq_schema import Faq_Schema
from models.faq import faq
from models.usuarios import usuarios
from vectorstore.vector_service import buscar_faq
from utils.pdf import descargar_pdf_telegram
from mcp.memory_client import MemoryClient
from models.documento_telegram import documentos_telegram
from vectorstore.vector_service import agregar_pdf_a_usuario
from vectorstore.vector_service import buscar_en_documentos_usuario
import os
import httpx
from utils.pdf_leer import extraer_texto_pdf

memory = MemoryClient("http://localhost:5005")

user = APIRouter()
chat = APIRouter()
test_usuarios = APIRouter()
telegram_router = APIRouter()  

CHATWOOT_URL = os.getenv("CHATWOOT_URL")
ACCOUNT_ID = os.getenv("CHATWOOT_ACCOUNT_ID")
API_TOKEN = os.getenv("CHATWOOT_API_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

chatwoot_conversations = {}

class ChatRequest(BaseModel):
    message: str
    session_id: str

class ChatResponse(BaseModel):
    answer: str

class ChatLoginRequest(BaseModel):
    id_usuario: int
    id_estudiante: int | None = None  

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

async def enviar_mensaje_telegram(chat_id: str, texto: str):
    async with httpx.AsyncClient() as client:
        await client.post(
            TELEGRAM_API_URL,
            json={"chat_id": chat_id, "text": texto}
        )

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

@test_usuarios.get("/test/usuarios")
def get_test_usuarios(db: Session = Depends(get_db)):
    stmt = select(usuarios)
    result = db.execute(stmt).fetchall()
    return {
        "total": len(result),
        "usuarios": [dict(row._mapping) for row in result]
    }

@user.post("/iniciar_chat")
async def iniciar_chat_endpoint(request: ChatLoginRequest):
    user_id = request.id_usuario
    id_estudiante = request.id_estudiante

    await memory.write(user_id, {
        "id_usuario": user_id,
        "id_estudiante": id_estudiante,
        "rol": "estudiante"
    })

    return {
        "message": "Sesión iniciada correctamente",
        "id_usuario": user_id,
        "id_estudiante": id_estudiante
    }

@chat.post("/chat", response_model=ChatResponse)
def chat_endpoint(payload: ChatRequest):
    user_id = payload.session_id
    state = {
        "messages": [{"role": "user", "content": payload.message}],
        "intent": "general",
        "context": "",
        
    }

    result = graph.invoke(
        state,
        config={"configurable": {"thread_id": str(user_id)}}
    )

    messages = result.get("messages", [])
    answer = messages[-1].content if messages else "No se pudo generar respuesta."
    return {"answer": answer}




@telegram_router.post("/telegram/webhook")
async def telegram_webhook(payload: dict, db: Session = Depends(get_db)):

    message_data = payload.get("message")
    if not message_data:
        return {"status": "ignored"}

    chat_id = str(message_data["chat"]["id"])
    user_message = message_data.get("text", "")

    query = usuarios.select().where(usuarios.c.telegram_id == chat_id)
    usuario = db.execute(query).first()

    document = message_data.get("document")

    
    if document and document.get("mime_type") == "application/pdf":

        if not usuario:
            await enviar_mensaje_telegram(chat_id, "Primero debes vincular tu cuenta.")
            return {"status": "no_linked"}

        user_id_bd = usuario.id
        file_id = document["file_id"]
        file_name = document.get("file_name", "documento.pdf")

        archivo_local = await descargar_pdf_telegram(file_id, chat_id, file_name)

        insert_query = documentos_telegram.insert().values(
            id_usuario=user_id_bd,
            nombre_original=file_name,
            ruta_archivo=archivo_local,
            mime_type=document.get("mime_type")
        )

        db.execute(insert_query)
        db.commit()

        texto_pdf = extraer_texto_pdf(archivo_local)

        agregar_pdf_a_usuario(
            user_id=user_id_bd,
            texto_pdf=texto_pdf,
            nombre_archivo=file_name
        )

        await enviar_mensaje_telegram(
            chat_id,
            f"Documento '{file_name}' recibido y procesado correctamente."
        )

        return {"status": "pdf_procesado"}

    
    if user_message:

        if not usuario:
            await enviar_mensaje_telegram(chat_id, "Primero debes vincular tu cuenta.")
            return {"status": "no_linked"}

        state = {
            "messages": [{"role": "user", "content": user_message}],
            "user_id": usuario.id
        }

        result = await graph.ainvoke(
            state,
            config={"configurable": {"thread_id": chat_id}}
        )

        messages = result.get("messages", [])
        bot_response = messages[-1].content if messages else "No se pudo generar respuesta."

        await enviar_mensaje_telegram(chat_id, bot_response)

        return {"status": "ok"}

    return {"status": "no_text_or_document"}