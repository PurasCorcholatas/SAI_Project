from config.db import SessionLocal
from embedding_service import eliminar_documento_completo

db = SessionLocal()

try:
    eliminar_documento_completo(
        nombre_archivo="Hola.pdf",
        user_id=3,
        db=db
    )
finally:
    db.close()