import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@db:5432/doc_ai")

MCP_SERVER_NAME = os.getenv("doc-ai-assistant")

API_BASE_URL = os.getenv("API_BASE_URL")

BOT_TOKEN = os.getenv("BOT_TOKEN")

WEBHOOK_BASE_URL = os.getenv("WEBHOOK_BASE_URL", "")
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/telegram/webhook")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")

WEB_SERVER_HOST = os.getenv("WEB_SERVER_HOST", "127.0.0.1")
WEB_SERVER_PORT = int(os.getenv("WEB_SERVER_PORT", "8080"))

def validate_bot_config() -> None:
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is not set")

    if not WEBHOOK_BASE_URL:
        raise RuntimeError("WEBHOOK_BASE_URL is not set")

    if not WEBHOOK_SECRET:
        raise RuntimeError("WEBHOOK_SECRET is not set")
