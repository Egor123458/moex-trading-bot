"""Сервис для запуска Telegram бота отдельным процессом"""

import asyncio
import logging
from config.settings import settings
from src.monitoring.telegram_bot import TelegramBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_telegram_bot():
    """Запуск Telegram бота"""
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
        logger.error("Telegram токен или chat_id не указаны в .env")
        return
    
    bot = TelegramBot(settings.TELEGRAM_BOT_TOKEN, settings.TELEGRAM_CHAT_ID)
    bot.start()


if __name__ == "__main__":
    run_telegram_bot()

