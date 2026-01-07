"""Интеграция с Tinkoff Invest API с поддержкой нескольких токенов"""

import logging
from datetime import datetime
from typing import Optional, Dict, List
import pandas as pd

try:
    from tinkoff.invest import Client, CandleInterval, OrderDirection, OrderType
    from tinkoff.invest.schemas import MoneyValue, Quotation
    TINKOFF_AVAILABLE = True
except ImportError:
    TINKOFF_AVAILABLE = False
    # Создаем заглушки для типов
    Client = None
    OrderDirection = None
    OrderType = None
    MoneyValue = None
    Quotation = None
    CandleInterval = None

from src.utils.token_manager import token_manager

logger = logging.getLogger(__name__)


class TinkoffAPIClient:
    """Клиент для Tinkoff Invest API с поддержкой нескольких токенов"""
    
    def __init__(self, token: Optional[str] = None, account_id: str = '', sandbox: bool = False):
        """
        Args:
            token: Конкретный токен (если None, используется TokenManager)
            account_id: ID счета
            sandbox: Использовать песочницу (True) или боевой (False)
        """
        if not TINKOFF_AVAILABLE:
            raise ImportError("Установите: pip install tinkoff-invest")
        
        self.account_id = account_id
        self.sandbox = sandbox
        self.token = token
        self.current_token = None
        self.logger = logging.getLogger(__name__)
        
        # Если токен не указан, используем менеджер
        if not self.token:
            self.token = token_manager.get_token(strategy='round_robin')
            if not self.token:
                raise ValueError("Нет доступных токенов Tinkoff!")
        
        self.current_token = self.token
        self.logger.info(f"TinkoffAPIClient инициализирован (sandbox={sandbox})")
    
    def _get_client(self) -> Client:
        """Получить клиент (контекстный менеджер)"""
        return Client(self.current_token, sandbox=self.sandbox)
    
    def switch_token(self):
        """Переключиться на другой токен (при ошибках)"""
        old_token = self.current_token
        self.current_token = token_manager.get_token(strategy='round_robin')
        if self.current_token != old_token:
            self.logger.info("Переключение на другой токен")
        return self.current_token
    
    def get_candles(
        self,
        figi: str,
        from_date: datetime,
        to_date: datetime,
        interval = None,
    ) -> pd.DataFrame:
        """
        Получить свечи через Tinkoff API.
        
        Args:
            figi: FIGI инструмента
            from_date: Начальная дата
            to_date: Конечная дата
            interval: CANDLE_INTERVAL_1_MIN, _5_MIN, _HOUR, _DAY (или None для значения по умолчанию)
        
        Returns:
            DataFrame с OHLCV
        """
        if interval is None:
            if TINKOFF_AVAILABLE and CandleInterval is not None:
                interval = CandleInterval.CANDLE_INTERVAL_HOUR
            else:
                # Fallback если библиотека не установлена
                logger.error("tinkoff.invest не установлен! Установите: pip install tinkoff-invest")
                return pd.DataFrame()
        
        max_retries = len(token_manager.get_all_tokens())
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                with self._get_client() as client:
                    candles = client.market_data.get_candles(
                        figi=figi,
                        from_=from_date,
                        to=to_date,
                        interval=interval,
                    )
                    
                    df = pd.DataFrame(
                        [
                            {
                                "time": c.time,
                                "open": self._quotation_to_float(c.open),
                                "high": self._quotation_to_float(c.high),
                                "low": self._quotation_to_float(c.low),
                                "close": self._quotation_to_float(c.close),
                                "volume": c.volume,
                            }
                            for c in candles.candles
                        ],
                    )
                    
                    return df
                    
            except Exception as e:
                self.logger.warning(f"Ошибка с токеном: {e}")
                token_manager.mark_token_failed(self.current_token)
                
                if retry_count < max_retries - 1:
                    self.switch_token()
                    retry_count += 1
                else:
                    raise
        
        return pd.DataFrame()
    
    def get_portfolio(self) -> Dict:
        """
        Получить текущий портфель.
        
        Returns:
            {'positions': [...], 'total_value': float, 'cash': float}
        """
        max_retries = len(token_manager.get_all_tokens())
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                with self._get_client() as client:
                    portfolio = client.operations.get_portfolio(account_id=self.account_id)
                    
                    positions = []
                    for pos in portfolio.positions:
                        positions.append(
                            {
                                "figi": pos.figi,
                                "ticker": self._get_ticker_by_figi(pos.figi, client),
                                "quantity": pos.quantity,
                                "current_price": self._quotation_to_float(pos.current_price),
                                "average_buy_price": self._quotation_to_float(
                                    pos.average_position_price,
                                ),
                            },
                        )
                    
                    return {
                        "positions": positions,
                        "total_value": self._money_to_float(portfolio.total_amount_portfolio),
                        "cash": self._money_to_float(portfolio.total_amount_currencies),
                    }
                    
            except Exception as e:
                self.logger.warning(f"Ошибка получения портфеля: {e}")
                token_manager.mark_token_failed(self.current_token)
                
                if retry_count < max_retries - 1:
                    self.switch_token()
                    retry_count += 1
                else:
                    raise
        
        return {"positions": [], "total_value": 0.0, "cash": 0.0}
    
    def place_market_order(
        self,
        figi: str,
        quantity: int,
        direction: OrderDirection | str,
    ) -> Dict:
        """
        Разместить рыночный ордер.
        
        Args:
            figi: FIGI инструмента
            quantity: Количество лотов
            direction: ORDER_DIRECTION_BUY / ORDER_DIRECTION_SELL или строка 'BUY'/'SELL'
        
        Returns:
            {'order_id': str, 'status': str, 'executed_price': float}
        """
        if isinstance(direction, str):
            if TINKOFF_AVAILABLE and OrderDirection is not None:
                direction = (
                    OrderDirection.ORDER_DIRECTION_BUY
                    if direction.upper() == "BUY"
                    else OrderDirection.ORDER_DIRECTION_SELL
                )
            else:
                logger.error("tinkoff.invest не установлен!")
                return {"order_id": "", "status": "FAILED", "lots_executed": 0, "executed_price": 0.0}
        
        max_retries = len(token_manager.get_all_tokens())
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                with self._get_client() as client:
                    order = client.orders.post_order(
                        figi=figi,
                        quantity=quantity,
                        direction=direction,
                        account_id=self.account_id,
                        order_type=OrderType.ORDER_TYPE_MARKET if OrderType else None,
                    )
                    
                    return {
                        "order_id": order.order_id,
                        "status": str(order.execution_report_status),
                        "lots_executed": order.lots_executed,
                        "executed_price": self._quotation_to_float(order.executed_order_price),
                    }
                    
            except Exception as e:
                self.logger.warning(f"Ошибка размещения ордера: {e}")
                token_manager.mark_token_failed(self.current_token)
                
                if retry_count < max_retries - 1:
                    self.switch_token()
                    retry_count += 1
                else:
                    raise
        
        return {"order_id": "", "status": "FAILED", "lots_executed": 0, "executed_price": 0.0}
    
    def get_figi_by_ticker(self, ticker: str) -> Optional[str]:
        """Получить FIGI по тикеру"""
        max_retries = len(token_manager.get_all_tokens())
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                with self._get_client() as client:
                    instruments = client.instruments.find_instrument(query=ticker)
                    if instruments.instruments:
                        return instruments.instruments[0].figi
                    return None
                    
            except Exception as e:
                self.logger.warning(f"Ошибка поиска FIGI: {e}")
                token_manager.mark_token_failed(self.current_token)
                
                if retry_count < max_retries - 1:
                    self.switch_token()
                    retry_count += 1
                else:
                    return None
        
        return None
    
    def _get_ticker_by_figi(self, figi: str, client: Client) -> Optional[str]:
        """Обратный поиск тикера по FIGI"""
        try:
            instruments = client.instruments.get_instrument_by(
                id_type=1,
                id=figi,
            )
            return instruments.instrument.ticker if instruments.instrument else None
        except Exception:
            return None
    
    @staticmethod
    def _quotation_to_float(q) -> float:
        """Конвертация Quotation в float"""
        if q is None:
            return 0.0
        if hasattr(q, 'units') and hasattr(q, 'nano'):
            return q.units + q.nano / 1e9
        return float(q) if q else 0.0
    
    @staticmethod
    def _money_to_float(m) -> float:
        """Конвертация MoneyValue в float"""
        if m is None:
            return 0.0
        if hasattr(m, 'units') and hasattr(m, 'nano'):
            return m.units + m.nano / 1e9
        return float(m) if m else 0.0
