import os
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from src.milo_supervisor import milo_app, get_clean_content_str

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🤖 **Agent Milo — Personal Assistant Online**\n\n"
        "I am Milo, your digital PA. Give me any order or task and I will deploy "
        "specialized sub-agents and tools to execute it for you.\n\n"
        "How can I assist you today?"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    chat_id = update.message.chat_id
    
    await update.message.reply_text("⚡ *Milo is working on your request...*", parse_mode="Markdown")
    
    try:
        initial_state = {"messages": [{"role": "user", "content": user_text}], "sub_tasks": [], "current_result": "", "final_output": ""}
        
        # Invoke Milo Supervisor graph asynchronously
        loop = asyncio.get_running_loop()
        output_state = await loop.run_in_executor(None, milo_app.invoke, initial_state)
        
        messages = output_state.get("messages", [])
        if messages:
            last_msg = messages[-1]
            response_text = get_clean_content_str(last_msg.get("content", ""))
        else:
            response_text = output_state.get("current_result", "Task completed.")
            
        # Send response back to user
        if len(response_text) > 4000:
            for chunk in [response_text[i:i+4000] for i in range(0, len(response_text), 4000)]:
                await update.message.reply_text(chunk)
        else:
            await update.message.reply_text(response_text)
            
    except Exception as e:
        await update.message.reply_text(f"❌ Error processing request: {str(e)}")

def run_telegram_bot():
    if not TELEGRAM_TOKEN:
        print("[Telegram Bot] Error: TELEGRAM_BOT_TOKEN not found in environment.")
        return

    print("Starting Agent Milo Telegram Bot...")
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    app.run_polling()

if __name__ == "__main__":
    run_telegram_bot()
