from pypdf import PdfReader

def extraer_texto_pdf(ruta_archivo: str) -> str:
    reader = PdfReader(ruta_archivo)
    texto_completo = ""

    for page in reader.pages:
        texto_completo += page.extract_text() or ""

    return texto_completo
