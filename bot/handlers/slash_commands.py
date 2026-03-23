"""Slash command handlers with real backend integration."""

import httpx
import sys
import os

sys.path.insert(0, "/root/se-toolkit-lab-7/bot")
from config import config

class LMSClient:
    def __init__(self):
        self.base_url = config.LMS_API_BASE_URL
        self.headers = {"Authorization": f"Bearer {config.LMS_API_KEY}"}
    
    async def get(self, endpoint: str, params: dict = None):
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{self.base_url}{endpoint}",
                params=params,
                headers=self.headers
            )
            return resp

lms = LMSClient()

async def start() -> str:
    return "🤖 Welcome to LMS Bot! I can help you check labs, scores, and more. Use /help to see available commands, or just ask me questions in plain language!"

async def help() -> str:
    return """📋 *Available commands:*

/start - Welcome message
/help - Show this help
/health - Check backend status
/labs - List available labs
/scores <lab> - Get per-task pass rates

*Natural language examples:*
• "what labs are available?"
• "show me scores for lab 4"
• "which lab has the lowest pass rate?"
• "who are the top 5 students in lab 3?"

Use /labs to see which labs are available."""

async def health() -> str:
    try:
        resp = await lms.get("/items/")
        if resp.status_code == 200:
            items = resp.json()
            return f"✅ Backend is healthy. {len(items)} items available."
        else:
            return f"⚠️ Backend error: HTTP {resp.status_code}"
    except httpx.ConnectError:
        return "❌ Backend error: connection refused. Check that Docker services are running."
    except Exception as e:
        return f"❌ Backend error: {str(e)}"

async def labs() -> str:
    try:
        resp = await lms.get("/items/")
        if resp.status_code != 200:
            return f"⚠️ Could not fetch labs: HTTP {resp.status_code}"
        
        items = resp.json()
        labs_list = [item for item in items if item.get('type') == 'lab']
        
        if not labs_list:
            return "No labs found in the database."
        
        result = "📚 *Available labs:*\n\n"
        for lab in labs_list:
            result += f"• {lab.get('lab', 'Unknown')} – {lab.get('title', 'No title')}\n"
        
        return result
    except Exception as e:
        return f"❌ Error fetching labs: {str(e)}"

async def scores(lab: str = None) -> str:
    if not lab:
        return "❌ Please specify a lab. Usage: /scores <lab>\nExample: /scores lab-01"
    
    try:
        resp = await lms.get(f"/analytics/pass-rates", params={"lab": lab})
        
        if resp.status_code == 404:
            return f"❌ Lab '{lab}' not found. Use /labs to see available labs."
        if resp.status_code != 200:
            return f"⚠️ Could not fetch scores: HTTP {resp.status_code}"
        
        data = resp.json()
        
        if not data:
            return f"📊 No data available for {lab}. The ETL sync may need to run."
        
        result = f"📊 *Pass rates for {lab}:*\n\n"
        
        for task in data:
            task_name = task.get('task', 'Unknown')
            pass_rate = task.get('pass_rate', 0)
            attempts = task.get('attempts', 0)
            result += f"• *{task_name}*: {pass_rate:.1f}% ({attempts} attempts)\n"
        
        return result
    except Exception as e:
        return f"❌ Error fetching scores: {str(e)}"
