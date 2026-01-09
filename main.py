#!/usr/bin/env python3
"""
Главная точка входа торгового бота MOEX
Поддержка одновременной работы sandbox и live моделей
"""

import sys
import time
import logging
import threading
from pathlib import Path
from datetime import datetime, timedelta

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
    from src.data_collection.database import DatabaseManager
    from src.data_collection.moex_api import MOEXDataCollector
    from src.monitoring.bot_status_manager import BotStatusManager
    from src.brokers.broker_factory import create_broker
except ImportError as e:
    logger.error(f"Ошибка импорта: {e}")
    sys.exit(1)


class TradingBot:
    """Основной класс торгового бота с поддержкой dual mode"""
    
    def __init__(self):
        self.sandbox_client = None
        self.live_client = None
        self.db = None
        self.moex = None
        self.trading_enabled = True
        self.sandbox_capital = settings.trading.INITIAL_CAPITAL
        self.live_capital = settings.trading.INITIAL_CAPITAL
        
    def initialize(self):
        """Инициализация всех компонентов"""
        logger.info("="*60)
        logger.info("ИНИЦИАЛИЗАЦИЯ ТОРГОВОГО БОТА")
        logger.info("="*60)
        logger.info(f"Тип брокера: {settings.api.BROKER_TYPE}")
        logger.info(f"Режим: {settings.MODE}")
        
        broker_type = settings.api.BROKER_TYPE.lower()
        
        # Инициализация sandbox клиента
        if settings.MODE in ['paper_trading', 'dual_mode']:
            try:
                if broker_type == 'finam':
                    # Finam для sandbox (можно использовать тот же токен или отдельный счет)
                    finam_token = settings.api.FINAM_SANDBOX_TOKEN or settings.api.FINAM_TOKEN
                    finam_account = settings.api.FINAM_SANDBOX_ACCOUNT_ID or settings.api.FINAM_ACCOUNT_ID
                    if finam_token:
                        self.sandbox_client = create_broker(
                            broker_type='finam',
                            token=finam_token,
                            account_id=finam_account,
                            sandbox=True,
                            initial_capital=settings.trading.INITIAL_CAPITAL
                        )
                        logger.info("✅ Sandbox Finam клиент инициализирован")
                    else:
                        logger.warning("⚠️  Finam токен не указан для sandbox")
                elif broker_type == 'tinkoff':
                    # Tinkoff для sandbox
                    sandbox_tokens = sandbox_token_manager.get_all_tokens()
                    if sandbox_tokens:
                        self.sandbox_client = create_broker(
                            broker_type='tinkoff',
                            token=sandbox_token_manager.get_token(),
                            account_id=settings.api.TINKOFF_SANDBOX_ACCOUNT_ID or settings.api.TINKOFF_ACCOUNT_ID,
                            sandbox=True,
                            initial_capital=settings.trading.INITIAL_CAPITAL
                        )
                        logger.info("✅ Sandbox Tinkoff клиент инициализирован")
                    else:
                        logger.warning("⚠️  Tinkoff токены не указаны для sandbox")
                else:
                    # Paper Trading или другой брокер
                    self.sandbox_client = create_broker(
                        broker_type=broker_type,
                        token='',
                        account_id='',
                        sandbox=True,
                        initial_capital=settings.trading.INITIAL_CAPITAL
                    )
                    logger.info(f"✅ Sandbox {broker_type} клиент инициализирован")
            except Exception as e:
                logger.error(f"Ошибка инициализации sandbox клиента: {e}")
        
        # Инициализация live клиента
        if settings.MODE in ['live_trading', 'dual_mode']:
            try:
                if broker_type == 'finam':
                    # Finam для live
                    finam_token = settings.api.FINAM_LIVE_TOKEN or settings.api.FINAM_TOKEN
                    finam_account = settings.api.FINAM_LIVE_ACCOUNT_ID or settings.api.FINAM_ACCOUNT_ID
                    if finam_token:
                        self.live_client = create_broker(
                            broker_type='finam',
                            token=finam_token,
                            account_id=finam_account,
                            sandbox=False,
                            initial_capital=settings.trading.INITIAL_CAPITAL
                        )
                        logger.info("✅ Live Finam клиент инициализирован")
                    else:
                        logger.warning("⚠️  Finam токен не указан для live")
                elif broker_type == 'tinkoff':
                    # Tinkoff для live
                    live_tokens = live_token_manager.get_all_tokens()
                    if live_tokens:
                        self.live_client = create_broker(
                            broker_type='tinkoff',
                            token=live_token_manager.get_token(),
                            account_id=settings.api.TINKOFF_LIVE_ACCOUNT_ID or settings.api.TINKOFF_ACCOUNT_ID,
                            sandbox=False,
                            initial_capital=settings.trading.INITIAL_CAPITAL
                        )
                        logger.info("✅ Live Tinkoff клиент инициализирован")
                    else:
                        logger.warning("⚠️  Tinkoff токены не указаны для live")
                else:
                    # Paper Trading или другой брокер
                    self.live_client = create_broker(
                        broker_type=broker_type,
                        token='',
                        account_id='',
                        sandbox=False,
                        initial_capital=settings.trading.INITIAL_CAPITAL
                    )
                    logger.info(f"✅ Live {broker_type} клиент инициализирован")
            except Exception as e:
                logger.error(f"Ошибка инициализации live клиента: {e}")
        
        if not self.sandbox_client and not self.live_client:
            logger.error("❌ Не удалось инициализировать ни одного клиента!")
            return False
        
        # Инициализация БД
        try:
            self.db = DatabaseManager(settings.db.DATABASE_URL)
            logger.info(f"✅ Подключение к БД установлено")
        except Exception as e:
            logger.warning(f"⚠️  Проблема с подключением к БД: {e}")
        
        # Инициализация MOEX API
        try:
            self.moex = MOEXDataCollector()
            logger.info("✅ MOEX API инициализирован")
        except Exception as e:
            logger.warning(f"⚠️  Проблема с MOEX API: {e}")
        
        return True
    
    def get_portfolio_info(self, client, mode_name: str):
        """Получить информацию о портфеле"""
        try:
            portfolio = client.get_portfolio()
            capital = portfolio.get('total_value', 0)
            cash = portfolio.get('cash', 0)
            positions = portfolio.get('positions', [])
            positions_count = len(positions)
            
            logger.info(f"{mode_name} портфель: {capital:,.2f} ₽ (позиций: {positions_count})")
            
            # Обновление статуса
            if mode_name == "Sandbox":
                BotStatusManager.update_sandbox_capital(capital)
                BotStatusManager.update_sandbox_positions(positions)
            elif mode_name == "Live":
                BotStatusManager.update_live_capital(capital)
                BotStatusManager.update_live_positions(positions)
            
            return {
                'capital': capital,
                'cash': cash,
                'positions_count': positions_count,
                'positions': positions
            }
        except Exception as e:
            logger.warning(f"Ошибка получения {mode_name} портфеля: {e}")
            return None
    
    def trading_cycle_sandbox(self):
        """Торговый цикл для sandbox (тестирование или обучение)"""
        if not self.sandbox_client or not self.trading_enabled:
            return
        
        try:
            learning_only = settings.trading.SANDBOX_LEARNING_ONLY
            
            if learning_only:
                logger.info("--- Sandbox цикл обучения (без торговли) ---")
            else:
                logger.info("--- Sandbox торговый цикл ---")
            
            # Получение портфеля (для информации, даже в режиме обучения)
            portfolio_info = self.get_portfolio_info(self.sandbox_client, "Sandbox")
            if portfolio_info:
                self.sandbox_capital = portfolio_info['capital']
            
            # Сбор данных для обучения
            if self.moex and self.db:
                logger.info("Сбор данных для обучения...")
                try:
                    # Загрузка конфига тикеров
                    import yaml
                    with open('config/trading_config.yaml', 'r') as f:
                        config = yaml.safe_load(f)
                    tickers = config.get('tickers', {}).get('primary', ['SBER', 'GAZP', 'LKOH', 'GMKN'])
                    
                    # Сбор данных за последние 7 дней
                    end_date = datetime.now()
                    start_date = end_date - timedelta(days=7)
                    
                    for ticker in tickers:
                        try:
                            candles = self.moex.get_historical_candles(
                                ticker=ticker,
                                start_date=start_date,
                                end_date=end_date,
                                timeframe='1h'
                            )
                            
                            if not candles.empty and self.db:
                                # Сохранение в БД
                                for _, row in candles.iterrows():
                                    self.db.save_candle(
                                        ticker=ticker,
                                        time=row.get('time', row.get('begin', datetime.now())),
                                        open=row.get('open', 0),
                                        high=row.get('high', 0),
                                        low=row.get('low', 0),
                                        close=row.get('close', 0),
                                        volume=row.get('volume', 0),
                                        timeframe='1h'
                                    )
                                logger.info(f"✓ Собрано {len(candles)} свечей для {ticker}")
                        except Exception as e:
                            logger.warning(f"Ошибка сбора данных для {ticker}: {e}")
                    
                    logger.info("Данные собраны и сохранены в БД")
                except Exception as e:
                    logger.warning(f"Ошибка сбора данных: {e}")
            
            # Генерация сигналов (для анализа, без размещения ордеров в режиме обучения)
            logger.info("Генерация сигналов для анализа...")
            # TODO: Здесь будет логика генерации сигналов на основе ML моделей
            
            if learning_only:
                logger.info("✓ Sandbox цикл обучения завершен (торговля отключена)")
            else:
                # TODO: Размещение ордеров для sandbox (если режим обучения выключен)
                logger.info("Sandbox цикл завершен")
            
        except Exception as e:
            logger.error(f"Ошибка в sandbox цикле: {e}", exc_info=True)
    
    def trading_cycle_live(self):
        """Торговый цикл для live (реальная торговля)"""
        if not self.live_client or not self.trading_enabled:
            return
        
        try:
            logger.info("--- Live торговый цикл ---")
            
            # Получение портфеля
            portfolio_info = self.get_portfolio_info(self.live_client, "Live")
            if portfolio_info:
                self.live_capital = portfolio_info['capital']
            
            # TODO: Генерация сигналов и торговля для live
            # Здесь будет логика реальной торговли
            # Стратегии сначала тестируются на sandbox, затем применяются на live
            
            logger.info("Live цикл завершен")
            
        except Exception as e:
            logger.error(f"Ошибка в live цикле: {e}", exc_info=True)
    
    def trading_cycle(self):
        """Основной торговый цикл (выполняется для обоих режимов)"""
        logger.info(f"--- Торговый цикл ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ---")
        
        # Параллельное выполнение для sandbox и live
        if settings.MODE == 'dual_mode':
            # Оба режима одновременно
            thread_sandbox = threading.Thread(target=self.trading_cycle_sandbox)
            thread_live = threading.Thread(target=self.trading_cycle_live)
            
            thread_sandbox.start()
            thread_live.start()
            
            thread_sandbox.join()
            thread_live.join()
            
        elif settings.MODE == 'paper_trading':
            # Только sandbox
            self.trading_cycle_sandbox()
            
        elif settings.MODE == 'live_trading':
            # Только live
            self.trading_cycle_live()
        
        logger.info("Торговый цикл завершен")
    
    def run(self):
        """Запуск основного цикла бота"""
        logger.info("="*60)
        logger.info("ЗАПУСК ТОРГОВОГО БОТА MOEX AI")
        logger.info(f"Режим: {settings.MODE}")
        logger.info(f"Начальный капитал: {settings.trading.INITIAL_CAPITAL:,.0f} ₽")
        logger.info("="*60)
        
        if not self.initialize():
            logger.error("Не удалось инициализировать бота")
            return
        
        logger.info("✅ Бот запущен и работает")
        logger.info("Торговый цикл будет выполняться каждые 30 минут")
        
        # Основной цикл
        cycle_count = 0
        try:
            while True:
                cycle_count += 1
                logger.info(f"\n{'='*60}")
                logger.info(f"ТОРГОВЫЙ ЦИКЛ #{cycle_count}")
                logger.info(f"{'='*60}")
                
                self.trading_cycle()
                
                # Ожидание до следующего цикла (30 минут = 1800 секунд)
                logger.info("\nОжидание до следующего цикла (30 минут)...")
                time.sleep(1800)  # 30 минут
                
        except KeyboardInterrupt:
            logger.info("\nБот остановлен пользователем (Ctrl+C)")
        except Exception as e:
            logger.error(f"Критическая ошибка: {e}", exc_info=True)
            raise


def main():
    """Точка входа"""
    bot = TradingBot()
    bot.run()


if __name__ == "__main__":
    main()
