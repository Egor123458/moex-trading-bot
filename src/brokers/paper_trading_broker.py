"""
Paper Trading Broker - виртуальный брокер для тестирования без реального API
Имитирует торговлю на основе данных MOEX
"""

import logging
import pandas as pd
from datetime import datetime
from typing import Optional, Dict
import random

from src.brokers.base_broker import BaseBroker
from src.data_collection.moex_api import MOEXDataCollector

logger = logging.getLogger(__name__)


class PaperTradingBroker(BaseBroker):
    """Виртуальный брокер для paper trading (тестирование без реального API)"""
    
    def __init__(self, token: str = "", account_id: str = "", sandbox: bool = False, initial_capital: float = 1000000.0):
        """
        Args:
            token: Не используется
            account_id: Не используется
            sandbox: Не используется
            initial_capital: Начальный капитал
        """
        super().__init__(token, account_id, sandbox)
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions = {}  # {ticker: {'quantity': int, 'average_price': float}}
        self.moex = MOEXDataCollector()
        self.order_history = []
        self.logger.info(f"PaperTradingBroker инициализирован (капитал: {initial_capital:,.0f} ₽)")
    
    def get_portfolio(self) -> Dict:
        """Получить текущий портфель"""
        positions_list = []
        total_value = self.cash
        
        for ticker, pos in self.positions.items():
            # Получаем текущую цену с MOEX
            current_price = self.moex.get_current_price(ticker) or pos['average_price']
            
            position_value = pos['quantity'] * current_price
            total_value += position_value
            
            positions_list.append({
                "ticker": ticker,
                "quantity": pos['quantity'],
                "current_price": current_price,
                "average_buy_price": pos['average_price'],
            })
        
        return {
            "positions": positions_list,
            "total_value": total_value,
            "cash": self.cash
        }
    
    def place_market_order(
        self,
        ticker: str,
        quantity: int,
        direction: str
    ) -> Dict:
        """Разместить рыночный ордер (виртуальный)"""
        try:
            # Получаем текущую цену с MOEX
            current_price = self.moex.get_current_price(ticker)
            
            if not current_price:
                # Если цена не получена, используем среднюю цену позиции или случайную
                if ticker in self.positions:
                    current_price = self.positions[ticker]['average_price']
                else:
                    # Примерная цена для популярных тикеров
                    default_prices = {
                        'SBER': 300.0,
                        'GAZP': 200.0,
                        'LKOH': 7000.0,
                        'GMKN': 25000.0,
                        'YNDX': 3000.0
                    }
                    current_price = default_prices.get(ticker, 100.0)
            
            order_value = quantity * current_price
            
            if direction.upper() == "BUY":
                # Покупка
                if self.cash >= order_value:
                    self.cash -= order_value
                    
                    if ticker in self.positions:
                        # Пересчитываем среднюю цену
                        old_qty = self.positions[ticker]['quantity']
                        old_avg = self.positions[ticker]['average_price']
                        new_qty = old_qty + quantity
                        new_avg = ((old_qty * old_avg) + (quantity * current_price)) / new_qty
                        self.positions[ticker] = {
                            'quantity': new_qty,
                            'average_price': new_avg
                        }
                    else:
                        self.positions[ticker] = {
                            'quantity': quantity,
                            'average_price': current_price
                        }
                    
                    order_id = f"PAPER_{ticker}_{int(datetime.now().timestamp())}"
                    self.order_history.append({
                        'order_id': order_id,
                        'ticker': ticker,
                        'quantity': quantity,
                        'price': current_price,
                        'direction': 'BUY',
                        'timestamp': datetime.now()
                    })
                    
                    self.logger.info(f"📈 Paper Trade: BUY {quantity} {ticker} @ {current_price:.2f} ₽")
                    
                    return {
                        "order_id": order_id,
                        "status": "EXECUTED",
                        "lots_executed": quantity,
                        "executed_price": current_price
                    }
                else:
                    self.logger.warning(f"Недостаточно средств для покупки {quantity} {ticker}")
                    return {"order_id": "", "status": "FAILED", "lots_executed": 0, "executed_price": 0.0}
            
            else:  # SELL
                # Продажа
                if ticker in self.positions and self.positions[ticker]['quantity'] >= quantity:
                    self.cash += order_value
                    self.positions[ticker]['quantity'] -= quantity
                    
                    if self.positions[ticker]['quantity'] == 0:
                        del self.positions[ticker]
                    
                    order_id = f"PAPER_{ticker}_{int(datetime.now().timestamp())}"
                    self.order_history.append({
                        'order_id': order_id,
                        'ticker': ticker,
                        'quantity': quantity,
                        'price': current_price,
                        'direction': 'SELL',
                        'timestamp': datetime.now()
                    })
                    
                    self.logger.info(f"📉 Paper Trade: SELL {quantity} {ticker} @ {current_price:.2f} ₽")
                    
                    return {
                        "order_id": order_id,
                        "status": "EXECUTED",
                        "lots_executed": quantity,
                        "executed_price": current_price
                    }
                else:
                    self.logger.warning(f"Недостаточно позиций для продажи {quantity} {ticker}")
                    return {"order_id": "", "status": "FAILED", "lots_executed": 0, "executed_price": 0.0}
        
        except Exception as e:
            self.logger.error(f"Ошибка paper trading: {e}")
            return {"order_id": "", "status": "FAILED", "lots_executed": 0, "executed_price": 0.0}
    
    def get_figi_by_ticker(self, ticker: str) -> Optional[str]:
        """Получить FIGI по тикеру (для paper trading не требуется)"""
        return ticker
    
    def get_candles(
        self,
        ticker: str,
        from_date: datetime,
        to_date: datetime,
        interval: str = '1h'
    ) -> pd.DataFrame:
        """Получить исторические свечи через MOEX API"""
        return self.moex.get_historical_candles(ticker, from_date, to_date, interval)

