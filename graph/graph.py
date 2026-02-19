from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import ToolNode

from mcp.memory_client import memory
from langgraph.checkpoint.memory import MemorySaver

from typing import Literal, Annotated, Optional
from typing_extensions import TypedDict
from dotenv import load_dotenv
from tools.registry import tools

import smtplib
from email.mime.text import MIMEText
import os

from rag.search import buscar_faq

load_dotenv()

memory_saver = MemorySaver()


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
    user_id: Optional[int]
    thread_id: Optional[str]



llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.3
).bind_tools(tools)





def get_last_message_content(state: State):
    last = state["messages"][-1]
    return last["content"] if isinstance(last, dict) else last.content




async def verificar_sesion(state: State):
    thread_id = state.get("thread_id")

    if not thread_id:
        return {
            "messages": [{
                "role": "assistant",
                "content": "Error de sesión."
            }],
            "intent": "silencio"
        }

    try:
        memory_data = await memory.read(thread_id)
    except Exception as e:
        print("Error leyendo memoria:", e)
        return {}

    if isinstance(memory_data, dict):
        user_id = memory_data.get("id_usuario")
        if user_id:
            return {"user_id": user_id}

    return {}




def decidir_despues_sesion(state: State):
    return "router"




def router(state: State):

    if state.get("human_escalated"):
        return {"intent": "silencio"}

    mensaje = get_last_message_content(state).lower()

    if any(p in mensaje for p in ["asesor", "humano", "agente"]):
        return {"intent": "human"}

    prompt = f"""
Clasifica la intención del usuario en UNA sola palabra:

- human
- matricula
- buscar_correo
- faq
- general

Mensaje: {mensaje}
"""

    intent = llm.invoke(prompt).content.strip().lower()

    if intent not in ["human", "matricula", "buscar_correo", "faq", "general"]:
        intent = "general"

    return {"intent": intent}




def escalamiento_humano(state: State):

    msg = MIMEText("Se solicitó atención humana.")
    msg["Subject"] = "Caso escalado - SAI"
    msg["From"] = os.getenv("SMTP_EMAIL")
    msg["To"] = os.getenv("DESTINO_SOPORTE")

    try:
        with smtplib.SMTP(os.getenv("SMTP_HOST"), int(os.getenv("SMTP_PORT"))) as server:
            server.starttls()
            server.login(os.getenv("SMTP_EMAIL"), os.getenv("SMTP_PASSWORD"))
            server.send_message(msg)
    except:
        pass

    return {
        "messages": [{
            "role": "assistant",
            "content": "He notificado a un asesor humano. En breve continuará contigo."
        }],
        "human_escalated": True
    }


def silencio(state: State):
    return {"messages": []}




def rag_faq(state: State):
    question = get_last_message_content(state)
    context = buscar_faq(question)
    if not context:
        context = "No encontré información en preguntas frecuentes."
    return {"context": context}


def faq_response(state: State):
    system_prompt = f"Responde usando solo esta información:\n\n{state.get('context')}"
    response = llm.invoke([("system", system_prompt)] + state["messages"])
    return {"messages": [response]}




def chat_general(state: State):

    system_prompt = """
Eres un asistente del Sistema Académico Integral (SAI).

Reglas IMPORTANTES:

- Si el usuario quiere matricularse:
  1. Explica el proceso.
  2. Pregunta si desea continuar.
  3. Si responde afirmativamente (sí, claro, ok, continuar, etc.),
     llama la herramienta registrar_matricula.

- Si quiere consultar notas o correo:
  Usa el user_id si está disponible.
  Llama la herramienta correspondiente.

- Solo llama herramientas cuando tengas todos los datos.
- Si falta información, solicítala primero.
- No inventes datos.
- Mantén continuidad en la conversación.
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


tool_node = ToolNode(tools)


builder = StateGraph(State)

builder.add_node("verificar_sesion", verificar_sesion)
builder.add_node("router", router)
builder.add_node("escalamiento_humano", escalamiento_humano)
builder.add_node("chat_general", chat_general)
builder.add_node("tools", tool_node)
builder.add_node("rag_faq", rag_faq)
builder.add_node("faq_response", faq_response)
builder.add_node("silencio", silencio)


builder.add_edge(START, "verificar_sesion")

builder.add_conditional_edges(
    "verificar_sesion",
    decidir_despues_sesion,
    {
        "router": "router"
    }
)

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

graph = builder.compile(
    checkpointer=memory_saver
)
