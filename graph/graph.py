from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from sqlalchemy import text
from config.db import engine
from config.queries import obtener_docentes
from typing import Literal, Annotated, Optional
from typing_extensions import TypedDict
from dotenv import load_dotenv

import smtplib
from email.mime.text import MIMEText
import os



from rag.search import buscar_faq, buscar_en_embeddings
from services.db_service import (
    
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
    obtener_usuarios,
)

import re
load_dotenv()


class State(TypedDict):
    messages: Annotated[list, add_messages]
    intent: str
    context: str
    human_escalated: bool
    flow_step: Optional[str]
    collected_data: dict


llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.8
)


def clean_sql(query: str) -> str:
    return re.sub(r"```sql|```", "", query, flags=re.IGNORECASE).strip()





def get_last_message_content(state: State):
    last = state["messages"][-1]

    if isinstance(last, dict):
        return last["content"]
    else:
        return last.content





def router(state: State):
    last_message = get_last_message_content(state)


    prompt = f"""
Clasifica la intención del mensaje del usuario.
Responde SOLO con una palabra exacta:

- human → quiere hablar con una persona real
- matricula → quiere matricularse
- buscar_correo → olvidó su correo registrado
- faq → pregunta frecuente académica
- db_docentes → consulta sobre docentes
- db_cursos → consulta sobre cursos
- general → conversación normal

Mensaje:
"{last_message}"
"""

    intent = llm.invoke(prompt).content.strip().lower()

    valid_intents = [
        "human",
        "matricula",
        "buscar_correo",
        "faq",
        "db_docentes",
        "db_cursos",
        "general"
    ]

    if intent not in valid_intents:
        intent = "general"

    return {
        "intent": intent,
        "human_escalated": False,
        "flow_step": "",
        "collected_data": {}
    }



def generar_resumen_conversacion(state: State) -> str:
    mensajes = []
    for m in state['messages']:
        # m puede ser dict o HumanMessage/AIMessage, usa get_last_message_content similar:
        if isinstance(m, dict):
            mensajes.append(m.get("content", ""))
        else:
            mensajes.append(m.content)

    prompt = f"""
    Resumir la siguiente conversación de manera clara y breve para que un humano pueda entender el contexto sin leer cada mensaje literal:

    Mensajes:
    {mensajes}

    Resumen:
    """
    resumen = llm.invoke(prompt).content.strip()
    return resumen




def enviar_correo_escalamiento(state: State, chatwoot_link: str):
    resumen = generar_resumen_conversacion(state)

    cuerpo = f"""
Se ha solicitado atención humana.

Resumen de la conversación:
-----------------------
{resumen}
-----------------------

Link Chatwoot:
{chatwoot_link}
"""
    msg = MIMEText(cuerpo)
    msg["Subject"] = "Nuevo caso escalado a humano - SAI"
    msg["From"] = os.getenv("SMTP_EMAIL")
    msg["To"] = os.getenv("DESTINO_SOPORTE")

    with smtplib.SMTP(os.getenv("SMTP_HOST"), int(os.getenv("SMTP_PORT"))) as server:
        server.starttls()
        server.login(os.getenv("SMTP_EMAIL"), os.getenv("SMTP_PASSWORD"))
        server.send_message(msg)


def escalamiento_humano(state: State):

    chatwoot_link = "https://TU_CHATWOOT_URL/app/accounts/1/conversations"

    enviar_correo_escalamiento(state, chatwoot_link)

    return {
        "messages": [{
            "role": "assistant",
            "content": "Ya he notificado a un asesor humano. En breve continuará la conversación contigo."
        }],
        "human_escalated": True
    }


def chat_general(state: State):
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

def db_query_general(state):

    pregunta = state["messages"][-1].content.lower()
    resultados = None

    from config.db import engine

    with engine.begin() as conn:

        if "curso" in pregunta:
            resultados = obtener_cursos(conn)
            
        elif "docente" in pregunta:
            resultados = obtener_docentes(conn)
            
        elif "estudiante" in pregunta:
            resultados = obtener_estudiantes(conn)
            
        elif "faq" in pregunta:
            resultados = obtener_faq(conn)
            
        elif "grupo" in pregunta:
            resultados = obtener_grupos(conn)
            
        elif "log" in pregunta:
            resultados = obtener_logs_interacciones(conn)
            
        elif "materia" in pregunta:
            resultados = obtener_materias(conn)
            
        elif "matricula" in pregunta:
            resultados = obtener_matriculas(conn)
            
        elif "nota" in pregunta:
            resultados = obtener_notas(conn)
            
        elif "periodo" in pregunta:
            resultados = obtener_periodos(conn)
            
        elif "programa" in pregunta:
            resultados = obtener_programas(conn)
            
        elif "rol" in pregunta:
            resultados = obtener_roles(conn)
            
        elif "solicitud" in pregunta:
            resultados = obtener_solicitudes(conn)
            
        elif "usuario" in pregunta:
            resultados = obtener_usuarios(conn)
        

    if not resultados:
        return {"context": "No encontré información."}

    return {"context": resultados}




def db_query_docentes(state: State):
    db = state.get("configurable", {}).get("db")
    if db is None:
        return {"messages": ["No hay sesión de base de datos disponible."]}

    docentes = obtener_docentes(db)
    if not docentes:
        respuesta = "No hay docentes registrados."
    else:
        respuesta = "Docentes: " + ", ".join(docentes)
    return {"messages": [respuesta]}


def sql_node(state: State):
    query = state["messages"][-1].content
    query = clean_sql(query)
    print("SQL GENERADO:", query)

    try:
        with engine.begin() as conn:
            result = conn.execute(text(query))
            rows = result.fetchall()
            keys = result.keys()
            rows_dict = [dict(zip(keys, row)) for row in rows]
    except Exception as e:
        return {"messages": [f"Error ejecutando la consulta: {str(e)}"]}

    return {"context": rows_dict}

def sql_response(state: State):
    data = state.get("context", [])
    if not data:
        return {"messages": ["No se encontraron datos."]}

    primera_fila = data[0]
    columna_nombre = None
    for key in primera_fila.keys():
        if "nombre" in key.lower():
            columna_nombre = key
            break

    if columna_nombre:
        nombres = [str(row[columna_nombre]) for row in data]
        respuesta = "Los docentes activos son: " + ", ".join(nombres)
    else:
        respuesta = f"Se encontraron {len(data)} registros."
    return {"messages": [respuesta]}

def rag_faq(state: State):
    question = state["messages"][-1].content
    context = buscar_faq(question)
    if not context:
        context = "No se encontró información relevante en las preguntas frecuentes."
    return {"context": context}

def rag_embeddings(state: State):
    question = state["messages"][-1].content
    context_list = buscar_en_embeddings(question)
    if not context_list:
        context_list = ["No se encontró información relevante."]
    return {"context": "\n".join(context_list)}

def llm_bd(state: State):
    system_prompt = f"""
Eres SAI, un asistente académico profesional.

REGLAS:
- Responde SOLO usando los datos entregados.
- Si la lista contiene nombres, entrégalos de forma clara.
- No inventes información.
- Usa un tono humano y directo.

Depende de la pregunta formulada por el usuario, darla de manera adecuada.
Solo responde la pregunta por el usuario lo que pide si hay mas datos y no fueron lo que pidio no los muestres

Datos:
----------------
{state['context']}
----------------
"""
    response = llm.invoke([("system", system_prompt)] + state["messages"])
    return {"messages": [response]}

def faq_academico(state: State):
    system_prompt = f"""
Eres un asistente académico del SAI.
Responde usando solo la información del contexto.
No inventes datos ni copies el texto literal.
Usa un tono claro y cercano.

Da una respuesta clara.
Si aplica, sugiere próximos pasos.
Si falta información, dilo amablemente y ofrece ayuda.

Contexto:
----------------
{state['context']}
----------------
"""
    response = llm.invoke([("system", system_prompt)] + state["messages"])
    return {"messages": [response]}







def matricula_flujo(state: State):

    last_message = get_last_message_content(state)
    flow_step = state.get("flow_step")
    data = state.get("collected_data", {})

    if flow_step == "ask_identification":
        data["identificador"] = last_message

    with engine.begin() as conn:
        estudiante = conn.execute(
            text("SELECT * FROM estudiantes WHERE nombre=:ident OR documento=:ident"),
            {"ident": last_message}
        ).fetchone()

    if estudiante:
        respuesta = f"Hola {estudiante['nombre']}, ya estás registrado. Puedes matricularte en los cursos disponibles este periodo."
    else:
        respuesta = "No encontré un estudiante con esos datos. Por favor verifica tu nombre o documento."

    return {
        "messages": [{"role": "assistant", "content": respuesta}],
        "flow_step": "completed",
        "collected_data": data
    }


   

def buscar_correo_flujo(state: State):
    last_message = get_last_message_content(state)
    flow_step = state.get("flow_step")
    data = state.get("collected_data", {})

    if not flow_step:
        # Primera interacción: preguntar por el nombre o documento
        return {
            "messages": [{
                "role": "assistant",
                "content": "Puedo ayudarte a buscar tu correo registrado. ¿Prefieres darme tu nombre completo o tu número de documento?"
            }],
            "flow_step": "ask_identification",
            "collected_data": data
        }

    elif flow_step == "ask_identification":
        # Ya tengo el dato del usuario, lo guardo y busco en DB
        data["identificador"] = last_message.strip()

        with engine.begin() as conn:
            correo_real = conn.execute(
                text("SELECT email FROM usuarios WHERE nombre=:ident"),
                {"ident": data["identificador"]}
            ).fetchone()

        if correo_real:
            correo_encontrado = correo_real[0]
            respuesta = f"El correo registrado es: {correo_encontrado}"
        else:
            respuesta = "No pude encontrar un correo con esa información. Verifica que tu nombre esté correcto."

        return {
            "messages": [{"role": "assistant", "content": respuesta}],
            "flow_step": "completed",
            "collected_data": data
        }


    return {"messages": [{"role": "assistant", "content": "Continuemos."}]}



builder = StateGraph(State)

builder.add_node("router", router)
builder.add_node("escalamiento_humano", escalamiento_humano)
builder.add_node("matricula_flujo", matricula_flujo)
builder.add_node("buscar_correo_flujo", buscar_correo_flujo)
builder.add_node("chat_general", chat_general)
builder.add_node("rag_faq", rag_faq)
builder.add_node("faq_academico", faq_academico)

builder.add_edge(START, "router")

builder.add_conditional_edges(
    "router",
    lambda state: state["intent"],
    {
        "human": "escalamiento_humano",
        "matricula": "matricula_flujo",
        "buscar_correo": "buscar_correo_flujo",
        "faq": "rag_faq",
        "general": "chat_general",
    }
)

builder.add_edge("rag_faq", "faq_academico")

builder.add_edge("faq_academico", END)
builder.add_edge("chat_general", END)
builder.add_edge("escalamiento_humano", END)
builder.add_edge("matricula_flujo", END)
builder.add_edge("buscar_correo_flujo", END)

memory = MemorySaver()
graph = builder.compile(checkpointer=memory)
