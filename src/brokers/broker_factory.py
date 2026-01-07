"""
Фабрика для создания брокеров
Позволяет легко переключаться между разными брокерами
"""

import logging
from typing import Optional
from src.brokers.base_broker import BaseBroker
from src.brokers.paper_trading_broker import PaperTradingBroker

logger = logging.getLogger(__name__)


def create_broker(
    broker_type: str = "paper",
    token: str = "",
    account_id: str = "",
    sandbox: bool = False,
    initial_capital: float = 1000000.0
) -> BaseBroker:
    """
    Создать экземпляр брокера
    
    Args:
        broker_type: Тип брокера ('paper', 'tinkoff', 'finam', 'alor')
        token: API токен
        account_id: ID счета
        sandbox: Режим песочницы
        initial_capital: Начальный капитал (для paper trading)
    
    Returns:
        Экземпляр брокера
    """
    broker_type = broker_type.lower()
    
    if broker_type == "paper":
        logger.info("Создание Paper Trading Broker")
        return PaperTradingBroker(
            token=token,
            account_id=account_id,
            sandbox=sandbox,
            initial_capital=initial_capital
        )
    
    elif broker_type == "tinkoff":
        try:
            from src.data_collection.tinkoff_api import TinkoffAPIClient
            logger.info("Создание Tinkoff Broker")
            # Используем TinkoffAPIClient как брокер
            tinkoff_client = TinkoffAPIClient(token=token, account_id=account_id, sandbox=sandbox)
            return TinkoffBrokerWrapper(tinkoff_client)
        except ImportError as e:
            logger.warning(f"Tinkoff API недоступен: {e}, используем Paper Trading")
            return PaperTradingBroker(
                token=token,
                account_id=account_id,
                sandbox=sandbox,
                initial_capital=initial_capital
            )
        except Exception as e:
            logger.warning(f"Ошибка создания Tinkoff Broker: {e}, используем Paper Trading")
            return PaperTradingBroker(
                token=token,
                account_id=account_id,
                sandbox=sandbox,
                initial_capital=initial_capital
            )
    
    elif broker_type == "finam":
        try:
            from src.brokers.finam_broker import FinamBroker
            logger.info("Создание Finam Broker")
            return FinamBroker(token=token, account_id=account_id, sandbox=sandbox)
        except Exception as e:
            logger.warning(f"Finam Broker недоступен: {e}, используем Paper Trading")
            return PaperTradingBroker(
                token=token,
                account_id=account_id,
                sandbox=sandbox,
                initial_capital=initial_capital
            )
    
    elif broker_type == "alor":
        try:
            from src.brokers.alor_broker import AlorBroker
            logger.info("Создание Alor Broker")
            return AlorBroker(token=token, account_id=account_id, sandbox=sandbox)
        except Exception as e:
            logger.warning(f"Alor Broker недоступен: {e}, используем Paper Trading")
            return PaperTradingBroker(
                token=token,
                account_id=account_id,
                sandbox=sandbox,
                initial_capital=initial_capital
            )
    
    else:
        logger.warning(f"Неизвестный тип брокера: {broker_type}, используем Paper Trading")
        return PaperTradingBroker(
            token=token,
            account_id=account_id,
            sandbox=sandbox,
            initial_capital=initial_capital
        )


class TinkoffBrokerWrapper(BaseBroker):
    """Обертка для TinkoffAPIClient, чтобы он соответствовал интерфейсу BaseBroker"""
    
    def __init__(self, tinkoff_client):
        import pandas as pd
        self.client = tinkoff_client
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def get_portfolio(self):
        return self.client.get_portfolio()
    
    def place_market_order(self, ticker: str, quantity: int, direction: str):
        figi = self.client.get_figi_by_ticker(ticker)
        if not figi:
            return {"order_id": "", "status": "FAILED", "lots_executed": 0, "executed_price": 0.0}
        return self.client.place_market_order(figi, quantity, direction)
    
    def get_figi_by_ticker(self, ticker: str):
        return self.client.get_figi_by_ticker(ticker)
    
    def get_candles(self, ticker: str, from_date, to_date, interval: str = '1h'):
        import pandas as pd
        figi = self.client.get_figi_by_ticker(ticker)
        if not figi:
            return pd.DataFrame()
        return self.client.get_candles(figi, from_date, to_date, interval)

