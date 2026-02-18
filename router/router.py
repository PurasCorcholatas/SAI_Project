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
from services.embedding_service import buscar_faq


import os
import httpx


from mcp.memory_client import MemoryClient
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
    """
    Inicializa la sesión del usuario en el servidor de memoria.
    """
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
        "thread_id": str(user_id)
    }

    result = graph.invoke(
        state,
        config={
            "configurable": {
                "thread_id": str(user_id)  
            }
        }
    )

    messages = result.get("messages", [])
    answer = messages[-1].content if messages else "No se pudo generar respuesta."
    return {"answer": answer}






async def enviar_mensaje_telegram(chat_id: str, texto: str):
    """Enviar mensaje al chat de Telegram"""
    async with httpx.AsyncClient() as client:
        await client.post(
            TELEGRAM_API_URL,
            json={
                "chat_id": chat_id,
                "text": texto
            }
        )


async def obtener_conversation_id(chat_id: str):
    """Devuelve el conversation_id de Chatwoot para un chat_id de Telegram.
    Si no existe, lo crea."""
    async with httpx.AsyncClient() as client:
        if chat_id in chatwoot_conversations:
            return chatwoot_conversations[chat_id]

       
        response = await client.post(
            f"{CHATWOOT_URL}/api/v1/accounts/{ACCOUNT_ID}/conversations",
            headers={"api_access_token": API_TOKEN},
            json={
                "source_id": chat_id,  
                "inbox_id": 1,  
                "contact": {"name": f"Telegram_{chat_id}"}
            }
        )
        data = response.json()
        conversation_id = data.get("id")
        chatwoot_conversations[chat_id] = conversation_id
        return conversation_id


@telegram_router.post("/telegram/webhook")
async def telegram_webhook(payload: dict):
    """Webhook para recibir mensajes de Telegram, responder con LangGraph y guardar todo en Chatwoot."""
    message_data = payload.get("message")
    if not message_data:
        return {"status": "ignored"}

    chat_id = message_data["chat"]["id"]
    user_message = message_data.get("text", "")

    
    state = {
        "messages": [{"role": "user", "content": user_message}],
        "intent": "general",
        "context": "",
        "thread_id": str(chat_id)
    }

    
    result = await graph.ainvoke(
        state,
        config={
            "configurable": {"thread_id": str(chat_id)}
        }
    )

    messages = result.get("messages", [])
    bot_response = messages[-1].content if messages else "No se pudo generar respuesta."

    
    await enviar_mensaje_telegram(chat_id, bot_response)

    
    try:
        async with httpx.AsyncClient() as client:
            
            if chat_id not in chatwoot_conversations:
                response = await client.post(
                    f"{CHATWOOT_URL}/api/v1/accounts/{ACCOUNT_ID}/conversations",
                    headers={"api_access_token": API_TOKEN},
                    json={
                        "source_id": chat_id,
                        "inbox_id": 1,  
                        "contact": {"name": f"Telegram_{chat_id}"}
                    }
                )
                data = response.json()
                conversation_id = data.get("id")
                chatwoot_conversations[chat_id] = conversation_id
            else:
                conversation_id = chatwoot_conversations[chat_id]

            
            await client.post(
                f"{CHATWOOT_URL}/api/v1/accounts/{ACCOUNT_ID}/conversations/{conversation_id}/messages",
                headers={"api_access_token": API_TOKEN},
                json={"content": user_message, "message_type": "incoming"}
            )

            
            await client.post(
                f"{CHATWOOT_URL}/api/v1/accounts/{ACCOUNT_ID}/conversations/{conversation_id}/messages",
                headers={"api_access_token": API_TOKEN},
                json={"content": bot_response, "message_type": "outgoing"}
            )

    except Exception as e:
        print("Error sincronizando con Chatwoot:", e)

    return {"status": "ok"}

