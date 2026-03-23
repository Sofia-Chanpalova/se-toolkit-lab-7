import sys
import os

sys.path.insert(0, "/root/se-toolkit-lab-7/bot")

from config import config
from router import router

# Импортируем существующие обработчики
from .slash_commands import start, help, health, labs, scores

# Для не-команд (plain text) используем LLM роутер
async def handle_plain_text(message: str) -> str:
    """Handle natural language queries with LLM router."""
    return await router.route(message)

# Экспортируем все команды
__all__ = ['start', 'help', 'health', 'labs', 'scores', 'handle_plain_text']
