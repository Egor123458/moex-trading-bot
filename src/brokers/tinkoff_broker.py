"""Интеграция с Tinkoff Invest API"""

from datetime import datetime
from typing import Optional, List, Dict
import logging

try:
    from tinkoff_invest import TinkoffInvestApi
    TINKOFF_AVAILABLE = True
except ImportError:
    TINKOFF_AVAILABLE = False

logger = logging.getLogger(__name__)


class TinkoffBroker:
    """Клиент для работы с Tinkoff Invest API"""
    
    def __init__(self, token: str, sandbox: bool = True):
        """
        Args:
            token: API токен Tinkoff
            sandbox: Использовать sandbox (демо-режим)
        """
        if not TINKOFF_AVAILABLE:
            raise ImportError("Установите: pip install tinkoff-invest")
        
        self.token = token
        self.sandbox = sandbox
        self.api = TinkoffInvestApi(token, sandbox=sandbox)
        
        logger.info(f"Tinkoff Broker инициализирован (sandbox={sandbox})")
    
    def get_portfolio(self) -> Dict:
        """Получить текущий портфель"""
        try:
            portfolio = self.api.get_portfolio()
            
            positions = []
            if portfolio and 'positions' in portfolio:
                for position in portfolio['positions']:
                    positions.append({
                        'ticker': position.get('ticker', 'N/A'),
                        'quantity': position.get('balance', 0),
                        'average_price': position.get('averagePositionPrice', {}).get('value', 0),
                        'current_price': position.get('expectedYield', {}).get('value', 0),
                    })
            
            return {
                'positions': positions,
                'total_value': portfolio.get('totalAmountPortfolio', {}).get('value', 0)
            }
        
        except Exception as e:
            logger.error(f"Ошибка получения портфеля: {e}")
            return None
    
    def place_market_order(self, ticker: str, quantity: int, operation: str = 'Buy') -> Optional[str]:
        """
        Разместить рыночную заявку
        
        Args:
            ticker: Тикер (например SBER)
            quantity: Количество лотов
            operation: 'Buy' или 'Sell'
        
        Returns:
            order_id или None
        """
        try:
            # Получаем FIGI по тикеру
            figi = self._get_figi_by_ticker(ticker)
            if not figi:
                logger.error(f"Не найден FIGI для {ticker}")
                return None
            
            response = self.api.market_order(figi, quantity, operation)
            
            if response and 'orderId' in response:
                logger.info(f"Заявка размещена: {operation} {ticker} {quantity} лотов")
                return response['orderId']
            
            return None
        
        except Exception as e:
            logger.error(f"Ошибка размещения заявки: {e}")
            return None
    
    def _get_figi_by_ticker(self, ticker: str) -> Optional[str]:
        """Получить FIGI по тикеру"""
        try:
            instruments = self.api.get_market_stocks()
            if instruments and 'instruments' in instruments:
                for instrument in instruments['instruments']:
                    if instrument.get('ticker') == ticker:
                        return instrument.get('figi')
            return None
        except Exception as e:
            logger.error(f"Ошибка поиска FIGI: {e}")
            return None
