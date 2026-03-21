import httpx
import sys
import os

# Добавляем путь к корню проекта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config

async def start() -> str:
    return "Welcome to LMS Bot! Use /help to see available commands."

async def help() -> str:
    return """Available commands:
/start - Welcome message
/help - Show this help
/health - Check backend status
/labs - List available labs
/scores <lab> - Get scores for a lab"""

async def health() -> str:
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(
                f"{config.LMS_API_BASE_URL}/items/",
                headers={"Authorization": f"Bearer {config.LMS_API_KEY}"}
            )
            if resp.status_code == 200:
                return "✅ Backend is healthy"
            else:
                return f"⚠️ Backend returned status {resp.status_code}"
    except Exception as e:
        return f"❌ Backend error: {str(e)}"

async def labs() -> str:
    return "Available labs: lab-01, lab-02, lab-03, lab-04, lab-05, lab-06, lab-07"

async def scores(lab: str = "lab-01") -> str:
    return f"Scores for {lab}: Not implemented yet (Task 2)"

# Command registry
COMMANDS = {
    "/start": start,
    "/help": help,
    "/health": health,
    "/labs": labs,
    "/scores": scores,
}
