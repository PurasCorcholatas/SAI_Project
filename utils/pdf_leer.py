import re
from pypdf import PdfReader

def extraer_texto_pdf(ruta_archivo: str) -> str:
    reader = PdfReader(ruta_archivo)
    texto_completo = ""

    for page in reader.pages:
        texto = page.extract_text() or ""
        texto_completo += texto + "\n"

    
    texto_completo = re.sub(r"\s+", " ", texto_completo)
    texto_completo = texto_completo.strip()

    return texto_completo