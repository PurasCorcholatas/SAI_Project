from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from sqlalchemy import text
from config.db import engine
from config.queries import obtener_docentes
from typing import Literal, Annotated
from typing_extensions import TypedDict
from dotenv import load_dotenv

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
    intent: Literal["general", "faq", "db"]
    context: str


llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.8
)


def clean_sql(query: str) -> str:
    return re.sub(r"```sql|```", "", query, flags=re.IGNORECASE).strip()


def router(state: State):
    last_message = state["messages"][-1].content
    prompt = f"""
Clasifica la intención del mensaje del usuario.
Responde SOLO con una palabra:

- faq → preguntas frecuentes académicas
- db → consultas sobre datos del sistema
- general → conversación normal

Mensaje:
"{last_message}"
"""
    intent = llm.invoke(prompt).content.strip().lower()
    if intent not in ["general", "faq", "db"]:
        intent = "general"
    return {"intent": intent}

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


builder = StateGraph(State)

builder.add_node("router", router)
builder.add_node("chat_general", chat_general)
builder.add_node("rag_faq", rag_faq)
builder.add_node("rag_embeddings", rag_embeddings)
builder.add_node("faq_academico", faq_academico)
builder.add_node("db_general", db_query_general)
builder.add_node("db_docentes", db_query_docentes)
builder.add_node("llm_bd", llm_bd)
builder.add_node("sql_node", sql_node)
builder.add_node("sql_response", sql_response)


builder.add_edge(START, "router")
builder.add_conditional_edges(
    "router",
    lambda state: state["intent"],
    {
        "faq": "rag_faq",
        "db": "db_general",
        "general": "chat_general",
    }
)
builder.add_edge("rag_faq", "faq_academico")
builder.add_edge("rag_embeddings", "faq_academico")
builder.add_edge("db_general", "llm_bd")
builder.add_edge("faq_academico", END)
builder.add_edge("llm_bd", END)
builder.add_edge("chat_general", END)
builder.add_edge("sql_node", "sql_response")
builder.add_edge("sql_response", END)
builder.add_edge("db_general", "chat_general")

# Memory
memory = MemorySaver()
graph = builder.compile(checkpointer=memory)
