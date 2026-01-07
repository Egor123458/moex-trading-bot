import os
from dataclasses import dataclass
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()


@dataclass
class APISettings:
    """Настройки API"""
    
    # Поддержка нескольких токенов Tinkoff (через запятую или перенос строки)
    TINKOFF_TOKENS: List[str] = None
    TINKOFF_SANDBOX_TOKENS: List[str] = None  # Токены для sandbox (тестирования)
    TINKOFF_LIVE_TOKENS: List[str] = None    # Токены для live (реальной торговли)
    TINKOFF_ACCOUNT_ID: str = os.getenv('TINKOFF_ACCOUNT_ID', '')
    TINKOFF_SANDBOX_ACCOUNT_ID: str = os.getenv('TINKOFF_SANDBOX_ACCOUNT_ID', '')
    TINKOFF_LIVE_ACCOUNT_ID: str = os.getenv('TINKOFF_LIVE_ACCOUNT_ID', '')
    MOEX_API_KEY: str = os.getenv('MOEX_API_KEY', '')  # Для ALGOPACK
    
    def __post_init__(self):
        """Парсинг токенов из переменных окружения"""
        # Парсинг sandbox токенов
        if self.TINKOFF_SANDBOX_TOKENS is None:
            sandbox_tokens_str = os.getenv('TINKOFF_SANDBOX_TOKENS', '')
            if sandbox_tokens_str:
                sandbox_tokens_str = sandbox_tokens_str.replace('\n', ',').replace(';', ',')
                self.TINKOFF_SANDBOX_TOKENS = [t.strip() for t in sandbox_tokens_str.split(',') if t.strip()]
            else:
                self.TINKOFF_SANDBOX_TOKENS = []
        
        # Парсинг live токенов
        if self.TINKOFF_LIVE_TOKENS is None:
            live_tokens_str = os.getenv('TINKOFF_LIVE_TOKENS', '')
            if live_tokens_str:
                live_tokens_str = live_tokens_str.replace('\n', ',').replace(';', ',')
                self.TINKOFF_LIVE_TOKENS = [t.strip() for t in live_tokens_str.split(',') if t.strip()]
            else:
                self.TINKOFF_LIVE_TOKENS = []
        
        # Обратная совместимость: если указан TINKOFF_TOKENS, используем его
        if self.TINKOFF_TOKENS is None:
            tokens_str = os.getenv('TINKOFF_TOKENS', os.getenv('TINKOFF_TOKEN', ''))
            if tokens_str:
                tokens_str = tokens_str.replace('\n', ',').replace(';', ',')
                tokens = [t.strip() for t in tokens_str.split(',') if t.strip()]
                self.TINKOFF_TOKENS = tokens
            else:
                self.TINKOFF_TOKENS = []
    
    def get_sandbox_tokens(self) -> List[str]:
        """Получить токены для sandbox"""
        return self.TINKOFF_SANDBOX_TOKENS if self.TINKOFF_SANDBOX_TOKENS else []
    
    def get_live_tokens(self) -> List[str]:
        """Получить токены для live"""
        return self.TINKOFF_LIVE_TOKENS if self.TINKOFF_LIVE_TOKENS else []
    
    def get_all_tokens(self) -> List[str]:
        """Получить все токены (для обратной совместимости)"""
        all_tokens = []
        all_tokens.extend(self.get_sandbox_tokens())
        all_tokens.extend(self.get_live_tokens())
        if not all_tokens and self.TINKOFF_TOKENS:
            all_tokens = self.TINKOFF_TOKENS
        return all_tokens


@dataclass
class DatabaseSettings:
    """Настройки БД"""
    DATABASE_URL: str = os.getenv('DATABASE_URL', 'sqlite:///data/trading_bot.db')
    POOL_SIZE: int = 5
    MAX_OVERFLOW: int = 10


@dataclass
class TradingSettings:
    """Торговые параметры"""
    INITIAL_CAPITAL: float = float(os.getenv('INITIAL_CAPITAL', 1_000_000))
    INVESTMENT_RATIO: float = 0.7
    TRADING_RATIO: float = 0.3
    MAX_POSITION_SIZE: float = 0.05  # 5% капитала
    MAX_DRAWDOWN: float = 0.15
    DAILY_LOSS_LIMIT: float = 0.03
    COMMISSION_RATE: float = 0.0004  # 0.04%


@dataclass
class MLSettings:
    """Настройки ML"""
    LOOKBACK_PERIOD: int = 60  # Период для признаков
    PREDICTION_HORIZON: int = 30  # На сколько минут вперед
    TRAIN_TEST_SPLIT: float = 0.8
    MODEL_RETRAIN_DAYS: int = 90


@dataclass
class RiskSettings:
    """Риск-менеджмент"""
    STOP_LOSS_PCT: float = 0.02  # 2%
    TAKE_PROFIT_PCT: float = 0.05  # 5%
    TRAILING_STOP_PCT: float = 0.015
    MAX_OPEN_POSITIONS: int = 5


class Settings:
    api = APISettings()
    db = DatabaseSettings()
    trading = TradingSettings()
    ml = MLSettings()
    risk = RiskSettings()
    
    MODE: str = os.getenv('MODE', 'paper_trading')
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    TELEGRAM_BOT_TOKEN: str = os.getenv('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_CHAT_ID: str = os.getenv('TELEGRAM_CHAT_ID', '')


settings = Settings()
