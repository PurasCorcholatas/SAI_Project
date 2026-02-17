from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import ToolNode
from sqlalchemy import text
from config.db import engine
from typing import Literal, Annotated, Optional
from typing_extensions import TypedDict
from dotenv import load_dotenv
from mcp.registry import tools
from langgraph.prebuilt import ToolNode
import smtplib
from email.mime.text import MIMEText
import os
import re

from rag.search import buscar_faq
from services.db_service import (
    
    obtener_docentes,
    obtener_estudiantes,
)

load_dotenv()



class State(TypedDict, total=False):
    messages: Annotated[list, add_messages]
    intent: Literal[
        "general",
        "faq",
        "human",
        "matricula",
        "buscar_correo",
        "silencio"
    ]
    context: str
    human_escalated: bool
    flow_step: Optional[str]
    collected_data: dict



llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.5
).bind_tools(tools)




def get_last_message_content(state: State):
    last = state["messages"][-1]
    return last["content"] if isinstance(last, dict) else last.content


def generar_resumen_conversacion(state: State) -> str:
    mensajes = []
    for m in state["messages"]:
        mensajes.append(m["content"] if isinstance(m, dict) else m.content)

    prompt = f"""
    Resume brevemente la siguiente conversación:

    {mensajes}
    """
    return llm.invoke(prompt).content.strip()


def enviar_correo_escalamiento(state: State):
    resumen = generar_resumen_conversacion(state)

    cuerpo = f"""
Se solicitó atención humana.

Resumen:
------------------
{resumen}
------------------
"""

    msg = MIMEText(cuerpo)
    msg["Subject"] = "Caso escalado - SAI"
    msg["From"] = os.getenv("SMTP_EMAIL")
    msg["To"] = os.getenv("DESTINO_SOPORTE")

    with smtplib.SMTP(os.getenv("SMTP_HOST"), int(os.getenv("SMTP_PORT"))) as server:
        server.starttls()
        server.login(os.getenv("SMTP_EMAIL"), os.getenv("SMTP_PASSWORD"))
        server.send_message(msg)




def router(state: State):

    if state.get("humano_escalado"):
        return {"intent": "silencio"}

    mensaje = get_last_message_content(state).lower()

    palabras_humano = ["asesor", "humano", "persona real", "agente"]

    if any(p in mensaje for p in palabras_humano):
        return {"intent": "human"}

    prompt = f"""
Clasifica la intención del usuario:

- human
- matricula
- buscar_correo
- faq
- general

Mensaje: {mensaje}
"""

    intent = llm.invoke(prompt).content.strip().lower()

    valid = ["human", "matricula", "buscar_correo", "faq", "general"]

    if intent not in valid:
        intent = "general"

    return {"intent": intent}




def escalamiento_humano(state: State):
    enviar_correo_escalamiento(state)
    return {
        "messages": [{
            "role": "assistant",
            "content": "He notificado a un asesor humano. En breve continuará contigo."
        }],
        "humano_escalado": True
    }


def silencio(state: State):
    return {"messages": []}


def chat_general(state):
    system_prompt = """
Eres un asistente del Sistema Académico Integral (SAI).

Reglas importantes:

- Si el usuario quiere consultar su matrícula o correo electrónico pero NO ha proporcionado
  su id_usuario, debes pedirlo antes de llamar la herramienta.

- Solo debes llamar las herramientas cuando tengas los datos necesarios.
- Si falta información, primero solicítala de forma clara y amable.

- Si el usuario pregunta cómo matricularse:
  1. Explica el proceso.
  2. Ofrece realizar la inscripción desde el chat.
  3. Si acepta, usa la herramienta registrar_matricula.

Mantén tono profesional.
No inventes información.
"""

    messages = state["messages"]

   
    if not any(isinstance(m, SystemMessage) for m in messages):
        messages = [SystemMessage(content=system_prompt)] + messages

    response = llm.invoke(messages)

    return {"messages": [response]}




def should_continue(state):
    last_message = state["messages"][-1]

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"

    return "end"


def rag_faq(state: State):
    question = get_last_message_content(state)
    context = buscar_faq(question)

    if not context:
        context = "No encontré información en preguntas frecuentes."

    return {"context": context}


def faq_response(state: State):

    system_prompt = f"""
Responde usando solo esta información:

{state.get('context')}
"""

    response = llm.invoke(
        [("system", system_prompt)] + state["messages"]
    )

    return {"messages": [response]}





tool_node = ToolNode(tools)


builder = StateGraph(State)

builder.add_node("router", router)
builder.add_node("escalamiento_humano", escalamiento_humano)
builder.add_node("chat_general", chat_general)
builder.add_node("tools", tool_node)
builder.add_node("rag_faq", rag_faq)
builder.add_node("faq_response", faq_response)
builder.add_node("silencio", silencio)

builder.add_edge(START, "router")

builder.add_conditional_edges(
    "router",
    lambda state: state["intent"],
    {
        "human": "escalamiento_humano",
        "faq": "rag_faq",
        "matricula": "chat_general",
        "buscar_correo": "chat_general",
        "general": "chat_general",
        "silencio": "silencio"
    }
)

builder.add_edge("rag_faq", "faq_response")

builder.add_edge("faq_response", END)
builder.add_edge("tools", "chat_general")
builder.add_conditional_edges(
    "chat_general",
    should_continue,
    {
        "tools": "tools",
        "end": END,
    },
)



builder.add_edge("escalamiento_humano", END)
builder.add_edge("silencio", END)

memory = MemorySaver()
graph = builder.compile(checkpointer=memory)
