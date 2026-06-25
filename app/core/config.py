import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@db:5432/doc_ai")

MCP_SERVER_NAME = os.getenv("doc-ai-assistant")

API_BASE_URL = os.getenv("API_BASE_URL")

if [DATABASE_URL, MCP_SERVER_NAME] is None:
    raise RuntimeError("DATABASE_URL or MCP_SERVER environment variable not set")
