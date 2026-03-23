#!/usr/bin/env python3
import argparse
import asyncio
import sys
import os
import inspect

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from handlers.commands import COMMANDS
from config import config

async def handle_command(command: str) -> str:
    """Parse and execute a command, return response text."""
    parts = command.strip().split()
    if not parts:
        return "No command provided"
    
    cmd = parts[0].lower()
    args = parts[1:] if len(parts) > 1 else []
    
    if cmd in COMMANDS:
        handler = COMMANDS[cmd]
        # Проверяем, является ли функция корутиной
        if inspect.iscoroutinefunction(handler):
            if args:
                return await handler(*args)
            return await handler()
        else:
            if args:
                return handler(*args)
            return handler()
    else:
        return f"❌ Unknown command: {cmd}. Use /help for available commands."

async def test_mode(command: str) -> None:
    """Run in test mode: execute command and print response."""
    try:
        response = await handle_command(command)
        print(response)
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", help="Run in test mode with a command")
    args = parser.parse_args()
    
    if args.test:
        asyncio.run(test_mode(args.test))
    else:
        print("🤖 Starting Telegram bot...")
        print("Use --test flag for testing commands")
        print("Example: uv run bot.py --test '/health'")
        # TODO: Task 2 - Add Telegram bot integration

if __name__ == "__main__":
    main()
