#!/usr/bin/env python3
import argparse
import asyncio
import sys
import os
import inspect
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from handlers.slash_commands import start, help, health, labs, scores
from router import router
from config import config

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def handle_command(command: str, args: list = None) -> str:
    """Parse and execute a command."""
    if command == "/start":
        return await start()
    elif command == "/help":
        return await help()
    elif command == "/health":
        return await health()
    elif command == "/labs":
        return await labs()
    elif command == "/scores":
        return await scores(args[0] if args else None)
    else:
        return f"❌ Unknown command: {command}. Use /help for available commands."

# Telegram handlers
async def telegram_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = await start()
    keyboard = [[InlineKeyboardButton("📊 View Labs", callback_data="labs"),
                 InlineKeyboardButton("📈 Top Students", callback_data="top")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(response, reply_markup=reply_markup)

async def telegram_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = await help()
    await update.message.reply_text(response, parse_mode='Markdown')

async def telegram_health(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = await health()
    await update.message.reply_text(response)

async def telegram_labs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = await labs()
    await update.message.reply_text(response, parse_mode='Markdown')

async def telegram_scores(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = ' '.join(context.args) if context.args else ''
    response = await scores(args if args else None)
    await update.message.reply_text(response, parse_mode='Markdown')

async def telegram_plain_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle natural language queries with LLM."""
    user_message = update.message.text
    await update.message.chat.send_action(action="typing")
    response = await router.route(user_message)
    await update.message.reply_text(response)

async def telegram_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline keyboard callbacks."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "labs":
        response = await labs()
        await query.edit_message_text(response, parse_mode='Markdown')
    elif query.data == "top":
        response = await router.route("who are the top 5 students?")
        await query.edit_message_text(response)

async def test_mode(command: str) -> None:
    """Run in test mode: execute command and print response."""
    try:
        if command.startswith("/"):
            parts = command.split()
            cmd = parts[0]
            args = parts[1:] if len(parts) > 1 else []
            response = await handle_command(cmd, args)
        else:
            response = await router.route(command)
        print(response)
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

def run_telegram_bot():
    """Run the Telegram bot."""
    if not config.BOT_TOKEN or config.BOT_TOKEN == "your-telegram-bot-token-here":
        print("❌ BOT_TOKEN not configured! Please set it in .env.bot.secret")
        sys.exit(1)
    
    app = Application.builder().token(config.BOT_TOKEN).build()
    
    # Command handlers
    app.add_handler(CommandHandler("start", telegram_start))
    app.add_handler(CommandHandler("help", telegram_help))
    app.add_handler(CommandHandler("health", telegram_health))
    app.add_handler(CommandHandler("labs", telegram_labs))
    app.add_handler(CommandHandler("scores", telegram_scores))
    
    # Plain text handler (for natural language)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, telegram_plain_text))
    
    # Callback handler for inline buttons
    app.add_handler(CallbackQueryHandler(telegram_callback))
    
    print("🤖 Bot is running! Press Ctrl+C to stop...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", help="Run in test mode with a command")
    args = parser.parse_args()
    
    if args.test:
        asyncio.run(test_mode(args.test))
    else:
        run_telegram_bot()

if __name__ == "__main__":
    main()
