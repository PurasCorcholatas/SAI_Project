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

from vectorstore.vector_service import buscar_faq
from vectorstore.vector_service import buscar_en_documentos_usuario

load_dotenv()

memory_saver = MemorySaver()

class State(TypedDict, total=False):
    messages: Annotated[list, add_messages]
    intent: Literal[
        "general",
        "faq",
        "documento",
        "human",
        "matricula",
        "buscar_correo",
        "silencio"
    ]
    context: Optional[str]
    human_escalated: bool
    user_id: Optional[int]
    thread_id: Optional[str]
    next_node: Optional[str]

classifier_llm = ChatOpenAI(
    model="gpt-4.1",
    temperature=0
)

llm = ChatOpenAI(
    model="gpt-4.1",
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
    except:
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

    history = state["messages"][-3:]
    conversation = "\n".join(
        [m["content"] if isinstance(m, dict) else m.content for m in history]
    )

    prompt = f"""
Eres un clasificador determinista.
Clasifica la intención del ÚLTIMO mensaje del usuario considerando el contexto.

Contexto:
"{conversation}"

Reglas:
- Si menciona documento, archivo, pdf, texto cargado -> documento
- Si habla de matricularse -> matricula
- Si pide humano -> human
- Si consulta notas/correo personal -> buscar_correo
- Si pregunta sobre el sistema -> faq
- En cualquier otro caso -> general

Responde SOLO una palabra.
"""

    raw_intent = classifier_llm.invoke(prompt).content.strip().lower()
    intent = raw_intent.split()[0].replace(".", "")

    valid = ["human","matricula","buscar_correo","faq","documento","general"]

    print("intent:", intent)
    
    if intent not in valid:
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

    system_prompt = f"""
Responde SOLO usando esta información:

{state.get('context')}

Si no está en el contexto, di que no tienes información.
"""

    response = llm.invoke([
        ("system", system_prompt),
        ("human", get_last_message_content(state))
    ])

    return {"messages": [response]}

def rag_documento(state: State):
    
    question = get_last_message_content(state)
    user_id = state.get("user_id")
    print("User_id:", user_id)

    if not user_id:
        return {
            "context": "",
            "next_node": "chat_general"
        }

    docs = buscar_en_documentos_usuario(
        user_id=user_id,
        query=question,
        k=8
    )

    if not docs:
        return {
            "context": "",
            "next_node": "chat_general"
        }

    contexto = "\n\n".join([doc.page_content for doc in docs[:4]])
    print("User_id:", user_id)
    print("Docs encontrados:", len(docs))
    print("Primer chunk:", docs[0].page_content if docs else "NADA")
    print("RAG se ejecuto")
    print("Contexto")

    return {
        "context": contexto,
        "next_node": "documento_response"
    }
    


def documento_response(state: State):
    question = get_last_message_content(state)
    context = state.get("context", "")

    print("Contexto:", len(context))
    print("Muestra del contexto:", context[:200] if context else "VACIO")

 
    
    if not context.strip():
        return {
            "messages": [{
                "role": "assistant",
                "content": "No encontré información suficiente en el documento."
            }]
        }

    system_prompt = f"""
Eres un asistente experto en análisis de documentos.

Responde usando la información del contexto.
No inventes información que no esté relacionada.

Si encuentras información parcialmente relacionada,
úsala para construir la mejor respuesta posible.

Solo responde "No encontré información suficiente en el documento."
si absolutamente nada del contexto está relacionado.

Contexto:
{context}
"""

    response = llm.invoke([
        ("system", system_prompt),
        ("human", question)
    ])

    return {"messages": [response]}

def chat_general(state: State):

    system_prompt = """
Eres un asistente del Sistema Académico Integral (SAI).
No inventes datos. Mantén continuidad.
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
builder.add_node("rag_documento", rag_documento)
builder.add_node("documento_response", documento_response)
builder.add_node("faq_response", faq_response)
builder.add_node("silencio", silencio)

builder.add_edge(START, "verificar_sesion")

builder.add_conditional_edges(
    "verificar_sesion",
    decidir_despues_sesion,
    {"router": "router"}
)

builder.add_conditional_edges(
    "router",
    lambda state: state["intent"],
    {
        "human": "escalamiento_humano",
        "faq": "rag_faq",
        "documento": "rag_documento",
        "matricula": "chat_general",
        "general": "chat_general",
        "silencio": "silencio"
    }
)

builder.add_conditional_edges(
    "rag_documento",
    lambda state: state.get("next_node"),
    {
        "documento_response": "documento_response",
        "chat_general": "chat_general"
    }
)

builder.add_edge("documento_response", END)
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

graph = builder.compile(checkpointer=memory_saver)