from pydantic import BaseModel

#Solo si quiero usarlo cuando es opcional una columna ejemplo ID
from typing import Optional



class Faq_Schema(BaseModel):
    pregunta: str
    respuesta: str
    categoria: str
    creado_en: str
    actualizado_en: str

