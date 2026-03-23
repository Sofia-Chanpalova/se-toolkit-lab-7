import os
from dotenv import load_dotenv

# Загружаем .env файл из родительской директории
load_dotenv("/root/se-toolkit-lab-7/.env.bot.secret")

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    LMS_API_BASE_URL = os.getenv("LMS_API_BASE_URL", "http://localhost:42002")
    LMS_API_KEY = os.getenv("LMS_API_KEY")
    LLM_API_KEY = os.getenv("LLM_API_KEY")
    LLM_API_BASE_URL = os.getenv("LLM_API_BASE_URL", "http://localhost:42005/v1")
    LLM_API_MODEL = os.getenv("LLM_API_MODEL", "coder-model")

config = Config()
