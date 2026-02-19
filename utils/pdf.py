import os
import httpx

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

STORAGE_PATH = "storage"
os.makedirs(STORAGE_PATH, exist_ok=True)

async def descargar_pdf_telegram(file_id: str, chat_id: str, file_name: str) -> str:
    """
    Descarga un PDF desde Telegram y lo guarda en storage/ con un nombre único por chat.
    Retorna la ruta local del archivo.
    """
    async with httpx.AsyncClient() as client:
        
        file_info_resp = await client.get(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getFile",
            params={"file_id": file_id}
        )
        file_info = file_info_resp.json()
        file_path = file_info["result"]["file_path"]

        
        file_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}"
        file_resp = await client.get(file_url)

        
        file_local_path = os.path.join(STORAGE_PATH, f"{chat_id}_{file_name}")
        with open(file_local_path, "wb") as f:
            f.write(file_resp.content)

        return file_local_path
