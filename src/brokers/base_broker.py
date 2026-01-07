"""
Базовый абстрактный класс для всех брокеров
Позволяет легко переключаться между разными брокерами
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BaseBroker(ABC):
    """Абстрактный базовый класс для всех брокеров"""
    
    def __init__(self, token: str = "", account_id: str = "", sandbox: bool = False):
        """
        Args:
            token: API токен
            account_id: ID счета
            sandbox: Режим песочницы
        """
        self.token = token
        self.account_id = account_id
        self.sandbox = sandbox
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def get_portfolio(self) -> Dict:
        """
        Получить текущий портфель
        
        Returns:
            {
                'positions': [{'ticker': str, 'quantity': int, 'current_price': float, ...}],
                'total_value': float,
                'cash': float
            }
        """
        pass
    
    @abstractmethod
    def place_market_order(
        self,
        ticker: str,
        quantity: int,
        direction: str  # 'BUY' or 'SELL'
    ) -> Dict:
        """
        Разместить рыночный ордер
        
        Args:
            ticker: Тикер инструмента (например, 'SBER')
            quantity: Количество лотов
            direction: 'BUY' или 'SELL'
        
        Returns:
            {
                'order_id': str,
                'status': str,
                'lots_executed': int,
                'executed_price': float
            }
        """
        pass
    
    @abstractmethod
    def get_figi_by_ticker(self, ticker: str) -> Optional[str]:
        """
        Получить FIGI по тикеру
        
        Args:
            ticker: Тикер (например, 'SBER')
        
        Returns:
            FIGI или None
        """
        pass
    
    @abstractmethod
    def get_candles(
        self,
        ticker: str,
        from_date: datetime,
        to_date: datetime,
        interval: str = '1h'
    ) -> 'pd.DataFrame':
        """
        Получить исторические свечи
        
        Args:
            ticker: Тикер
            from_date: Начальная дата
            to_date: Конечная дата
            interval: Таймфрейм ('1m', '5m', '1h', '1d')
        
        Returns:
            DataFrame с колонками: time, open, high, low, close, volume
        """
        pass
    
    def test_connection(self) -> bool:
        """
        Проверка подключения к брокеру
        
        Returns:
            True если подключение успешно
        """
        try:
            portfolio = self.get_portfolio()
            return portfolio is not None
        except Exception as e:
            self.logger.error(f"Ошибка подключения: {e}")
            return False

