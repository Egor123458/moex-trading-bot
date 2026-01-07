#!/usr/bin/env python3
"""
Главная точка входа торгового бота MOEX
"""

import sys
import time
import logging
from pathlib import Path
from datetime import datetime

# Добавляем корневую папку в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

try:
    from config.settings import settings
    from src.utils.token_manager import sandbox_token_manager, live_token_manager
except ImportError as e:
    logger.error(f"Ошибка импорта: {e}")
    sys.exit(1)


def main():
    """Основная функция запуска бота"""
    logger.info("="*60)
    logger.info("ЗАПУСК ТОРГОВОГО БОТА MOEX AI")
    logger.info(f"Режим: {settings.MODE}")
    logger.info(f"Начальный капитал: {settings.trading.INITIAL_CAPITAL:,.0f} ₽")
    logger.info("="*60)
    
    # Проверка токенов
    sandbox_tokens = sandbox_token_manager.get_all_tokens()
    live_tokens = live_token_manager.get_all_tokens()
    
    logger.info(f"Sandbox токенов: {len(sandbox_tokens)}")
    logger.info(f"Live токенов: {len(live_tokens)}")
    
    if not sandbox_tokens and not live_tokens:
        logger.error("❌ Нет доступных токенов! Проверьте .env файл")
        logger.info("Убедитесь, что в .env указаны:")
        logger.info("  TINKOFF_SANDBOX_TOKENS=ваш_токен")
        logger.info("  или")
        logger.info("  TINKOFF_LIVE_TOKENS=ваш_токен")
        return
    
    # Проверка подключения к БД
    try:
        from src.data_collection.database import DatabaseManager
        db = DatabaseManager(settings.db.DATABASE_URL)
        logger.info(f"✅ Подключение к БД: {settings.db.DATABASE_URL.split('@')[1] if '@' in settings.db.DATABASE_URL else 'локальная'}")
    except Exception as e:
        logger.warning(f"⚠️  Проблема с подключением к БД: {e}")
    
    logger.info("✅ Бот запущен и работает")
    logger.info("Торговый цикл будет выполняться каждые 30 минут")
    
    # Основной цикл
    cycle_count = 0
    try:
        while True:
            cycle_count += 1
            logger.info(f"--- Торговый цикл #{cycle_count} ---")
            logger.info(f"Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # TODO: Здесь будет основная логика торговли
            # Пока просто логируем, что бот работает
            
            # Ожидание до следующего цикла (30 минут = 1800 секунд)
            logger.info("Ожидание до следующего цикла (30 минут)...")
            time.sleep(1800)  # 30 минут
            
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем (Ctrl+C)")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
