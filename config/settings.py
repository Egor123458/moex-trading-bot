import os
from dataclasses import dataclass
from typing import List
from dotenv import load_dotenv

load_dotenv()


@dataclass
class APISettings:
    """Настройки API"""
    
    # Поддержка нескольких токенов Tinkoff (через запятую или перенос строки)
    TINKOFF_TOKENS: List[str] = None
    TINKOFF_ACCOUNT_ID: str = os.getenv('TINKOFF_ACCOUNT_ID', '')
    MOEX_API_KEY: str = os.getenv('MOEX_API_KEY', '')  # Для ALGOPACK
    
    def __post_init__(self):
        """Парсинг токенов из переменной окружения"""
        if self.TINKOFF_TOKENS is None:
            tokens_str = os.getenv('TINKOFF_TOKENS', os.getenv('TINKOFF_TOKEN', ''))
            
            # Поддержка нескольких форматов:
            # 1. Через запятую: token1,token2,token3
            # 2. Через перенос строки: token1\ntoken2\ntoken3
            # 3. Через точку с запятой: token1;token2;token3
            
            if tokens_str:
                # Замена переносов строк и точек с запятой на запятые
                tokens_str = tokens_str.replace('\n', ',').replace(';', ',')
                # Разделение по запятым и очистка
                tokens = [t.strip() for t in tokens_str.split(',') if t.strip()]
                self.TINKOFF_TOKENS = tokens
            else:
                self.TINKOFF_TOKENS = []
    
    def get_token(self, index: int = 0) -> str:
        """Получить токен по индексу (для ротации)"""
        if not self.TINKOFF_TOKENS:
            return ''
        return self.TINKOFF_TOKENS[index % len(self.TINKOFF_TOKENS)]
    
    def get_all_tokens(self) -> List[str]:
        """Получить все токены"""
        return self.TINKOFF_TOKENS if self.TINKOFF_TOKENS else []


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
