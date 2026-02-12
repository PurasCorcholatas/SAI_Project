from graph.graph import graph

def chat_sai(
    user_input: str,
    session_id: str
) -> str:
    """
    Punto único de entrada al LangGraph del SAI
    """

    config = {
        "configurable": {
            "thread_id": session_id
        }
    }

    result = graph.invoke(
        {"messages": [("user", user_input)]},
        config=config
    )

    return result["messages"][-1].content
