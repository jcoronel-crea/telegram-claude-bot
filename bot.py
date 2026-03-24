import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import anthropic

TELEGRAM_TOKEN = "PEGA_TU_TOKEN_AQUÍ"
ANTHROPIC_API_KEY = "PEGA_TU_API_KEY_AQUÍ"

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
logging.basicConfig(level=logging.INFO)
conversation_history = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Hola! Soy el asistente de AC TAXPROS. ¿En qué te puedo ayudar? 💬")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text
    if user_id not in conversation_history:
        conversation_history[user_id] = []
    conversation_history[user_id].append({"role": "user", "content": user_message})
    if len(conversation_history[user_id]) > 20:
        conversation_history[user_id] = conversation_history[user_id][-20:]
    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system="Eres un asistente de AC TAXPROS, empresa de impuestos y formación de negocios en Jackson Heights, NY. Respondes en español, con tono profesional y cercano. Para consultas específicas invitas al cliente a llamar al 347-538-5056.",
            messages=conversation_history[user_id]
        )
        assistant_reply = response.content[0].text
        conversation_history[user_id].append({"role": "assistant", "content": assistant_reply})
        await update.message.reply_text(assistant_reply)
    except Exception as e:
        await update.message.reply_text(f"Ocurrió un error: {str(e)}")

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conversation_history[user_id] = []
    await update.message.reply_text("Conversación reiniciada. 🔄")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot corriendo...")
    app.run_polling()
