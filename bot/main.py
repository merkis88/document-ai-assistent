import logging
import sys

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from app.bot.handlers import router
from app.core.config import (BOT_TOKEN, WEBHOOK_BASE_URL, WEBHOOK_PATH, WEBHOOK_SECRET, WEB_SERVER_HOST, WEB_SERVER_PORT)