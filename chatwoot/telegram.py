import httpx
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = "TU_TOKEN"
API_URL = "http://127.0.0.1:8000/api/chat"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hola! Soy el Soporte de ayuda de SAI. ¿En qué puedo ayudarte?"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    session_id = str(update.effective_user.id)

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                API_URL,
                json={
                    "message": user_message,
                    "session_id": session_id,
                },
            )

        if response.status_code != 200:
            await update.message.reply_text("Error del servidor.")
            return

        data = response.json()
        answer = data.get("answer", "No se pudo generar respuesta.")

        await update.message.reply_text(answer)

    except Exception:
        await update.message.reply_text("Error conectando con el servidor.")


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot corriendo...")
    app.run_polling()


if __name__ == "__main__":
    main()
