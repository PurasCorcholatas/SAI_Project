from mcp.memory_client import MemoryClient


memory = MemoryClient("http://localhost:5005")




def iniciar_chat():
    """
    Pide al usuario su id_usuario y opcionalmente id_estudiante
    y los guarda en MCP server.
    """
    user_id_input = input("Ingresa tu id_usuario: ").strip()
    if not user_id_input.isdigit():
        print("id_usuario inválido")
        return None

    user_id = int(user_id_input)

    id_estudiante_input = input("Ingresa tu id_estudiante (opcional, ""No tengo"" para omitir): ").strip()
    id_estudiante = int(id_estudiante_input) if id_estudiante_input.isdigit() else None

    
    memory.write(user_id, {
        "id_usuario": user_id,
        "id_estudiante": id_estudiante,
        "rol": "estudiante"  
    })

    print(f"Sesión iniciada para usuario {user_id}, id_estudiante: {id_estudiante}")
    return user_id

