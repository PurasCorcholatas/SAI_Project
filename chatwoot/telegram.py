# import requests
# from telegram import Update
# # from Telegram.ext import (
#     ApplicationBuilder,
#     CommandHandler,
#     MessageHandler,
#     ContextTypes,
#     filters,
# )

# TOKEN = "8475804694:AAHbJ2IRmhn4_OfkA9T_97WGMMLaWy-_xB8"
# API_URL = "http://127.0.0.1:8000/chat"  


# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await update.message.reply_text(
#         "Hola! Soy el Soporte de ayuda de SAI Serviunix. ¿En qué puedo ayudarte?"
#     )


# async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     user_message = update.message.text
#     session_id = str(update.effective_user.id)  # importante para memoria

#     try:
#         response = requests.post(
#             API_URL,
#             json={
#                 "message": user_message,
#                 "session_id": session_id,
#             },
#         )

#         data = response.json()
#         answer = data.get("answer", "No se pudo generar respuesta.")

#         await update.message.reply_text(answer)

#     except Exception as e:
#         await update.message.reply_text("Error conectando con el servidor.")


# def main():
#     app = ApplicationBuilder().token(TOKEN).build()

#     app.add_handler(CommandHandler("start", start))
#     app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

#     print("Bot corriendo...")
#     app.run_polling()


# if __name__ == "__main__":
#     main()
