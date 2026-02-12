from rag.search import buscar_faq

print("\n Probando FAISS...\n")

pregunta = "¿Cómo me registro?"
respuesta = buscar_faq(pregunta)

print(" Pregunta:")
print(pregunta)

print("\n Respuesta:")
print(respuesta)
