import os
import asyncio
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from src.milo_supervisor import milo_app, get_clean_content_str

load_dotenv()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger("TelegramBot")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🤖 Agent Milo — Personal Assistant Online\n\n"
        "I am Milo, your digital PA. Give me any order or task and I will deploy "
        "specialized sub-agents and tools to execute it for you.\n\n"
        "How can I assist you today?"
    )
    await update.message.reply_text(welcome_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_text = update.message.text
    chat_id = update.message.chat_id
    user_name = update.message.from_user.first_name if update.message.from_user else "User"
    
    logger.info(f"Received Telegram message from {user_name} ({chat_id}): '{user_text}'")
    
    status_msg = await update.message.reply_text("⚡ Milo is analyzing your request and deploying sub-agents...")
    
    try:
        initial_state = {
            "messages": [{"role": "user", "content": user_text}], 
            "sub_tasks": [], 
            "current_result": "", 
            "final_output": ""
        }
        
        # Invoke Milo Supervisor graph asynchronously
        loop = asyncio.get_running_loop()
        output_state = await loop.run_in_executor(None, milo_app.invoke, initial_state)
        
        messages = output_state.get("messages", [])
        if messages:
            last_msg = messages[-1]
            response_text = get_clean_content_str(last_msg.get("content", ""))
        else:
            response_text = output_state.get("current_result", "Task completed successfully.")
            
        # Delete temporary status message
        try:
            await status_msg.delete()
        except Exception:
            pass

        # Send response back to user in chunks without Markdown parse errors
        if len(response_text) > 4000:
            for chunk in [response_text[i:i+4000] for i in range(0, len(response_text), 4000)]:
                await update.message.reply_text(chunk)
        else:
            await update.message.reply_text(response_text)
            
    except Exception as e:
        logger.error(f"Error handling Telegram message: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error processing request: {str(e)}")

def run_telegram_bot():
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    if not token:
        print("[Telegram Bot] Error: TELEGRAM_BOT_TOKEN not found in environment.")
        return

    print("==================================================")
    print("  Agent Milo — Telegram Bot Listener Online      ")
    print("==================================================")
    
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    app.run_polling()

if __name__ == "__main__":
    run_telegram_bot()
