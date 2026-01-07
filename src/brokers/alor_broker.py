"""
Интеграция с Alor Open API
Документация: https://alor.dev/
"""

import logging
import requests
import pandas as pd
from datetime import datetime
from typing import Optional, Dict
import jwt
import time

from src.brokers.base_broker import BaseBroker

logger = logging.getLogger(__name__)


class AlorBroker(BaseBroker):
    """Клиент для Alor Open API"""
    
    def __init__(self, token: str = "", account_id: str = "", sandbox: bool = False):
        """
        Args:
            token: JWT токен Alor
            account_id: ID счета (например, 'L01-00000F00')
            sandbox: Режим песочницы
        """
        super().__init__(token, account_id, sandbox)
        self.base_url = "https://api.alor.ru" if not sandbox else "https://apidev.alor.ru"
        self.refresh_token = None
        self.logger.info(f"AlorBroker инициализирован (sandbox={sandbox})")
    
    def _get_headers(self) -> Dict[str, str]:
        """Получить заголовки с авторизацией"""
        if not self.token:
            return {}
        
        # Alor использует JWT токены
        headers = {
            "Authorization": f"Bearer {self.token}",
            "X-ALOR-REQID": str(int(time.time() * 1000))
        }
        return headers
    
    def get_portfolio(self) -> Dict:
        """Получить текущий портфель"""
        if not self.token or not self.account_id:
            self.logger.warning("Токен или account_id Alor не указаны")
            return {"positions": [], "total_value": 0.0, "cash": 0.0}
        
        try:
            url = f"{self.base_url}/md/v2/portfolios/{self.account_id}"
            response = requests.get(url, headers=self._get_headers(), timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                positions = []
                total_value = 0.0
                cash = 0.0
                
                # Парсинг ответа Alor
                if 'positions' in data:
                    for pos in data['positions']:
                        positions.append({
                            "ticker": pos.get('symbol', ''),
                            "quantity": pos.get('qty', 0),
                            "current_price": pos.get('currentPrice', 0.0),
                            "average_buy_price": pos.get('averagePrice', 0.0),
                        })
                        total_value += pos.get('equity', 0.0)
                
                cash = data.get('cash', 0.0)
                total_value = data.get('equity', 0.0)
                
                return {
                    "positions": positions,
                    "total_value": total_value,
                    "cash": cash
                }
        except Exception as e:
            self.logger.error(f"Ошибка получения портфеля Alor: {e}")
        
        return {"positions": [], "total_value": 0.0, "cash": 0.0}
    
    def place_market_order(
        self,
        ticker: str,
        quantity: int,
        direction: str
    ) -> Dict:
        """Разместить рыночный ордер"""
        if not self.token or not self.account_id:
            self.logger.error("Токен или account_id Alor не указаны!")
            return {"order_id": "", "status": "FAILED", "lots_executed": 0, "executed_price": 0.0}
        
        try:
            url = f"{self.base_url}/commandapi/warptrans/TRADE/v2/client/orders/actions/market"
            headers = self._get_headers()
            headers["Content-Type"] = "application/json"
            
            data = {
                "quantity": quantity,
                "side": "buy" if direction.upper() == "BUY" else "sell",
                "instrument": {
                    "symbol": ticker,
                    "exchange": "MOEX"
                },
                "user": {
                    "account": self.account_id
                }
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "order_id": result.get("orderId", ""),
                    "status": result.get("status", "UNKNOWN"),
                    "lots_executed": result.get("executedQuantity", 0),
                    "executed_price": result.get("executedPrice", 0.0)
                }
        except Exception as e:
            self.logger.error(f"Ошибка размещения ордера Alor: {e}")
        
        return {"order_id": "", "status": "FAILED", "lots_executed": 0, "executed_price": 0.0}
    
    def get_figi_by_ticker(self, ticker: str) -> Optional[str]:
        """Получить FIGI по тикеру (Alor использует тикеры напрямую)"""
        return ticker
    
    def get_candles(
        self,
        ticker: str,
        from_date: datetime,
        to_date: datetime,
        interval: str = '1h'
    ) -> pd.DataFrame:
        """Получить исторические свечи"""
        try:
            # Маппинг таймфреймов для Alor
            timeframe_map = {
                '1m': 60,
                '5m': 300,
                '15m': 900,
                '1h': 3600,
                '1d': 86400
            }
            
            tf = timeframe_map.get(interval, 3600)
            
            url = f"{self.base_url}/md/v2/candles"
            params = {
                "symbol": ticker,
                "exchange": "MOEX",
                "from": int(from_date.timestamp()),
                "to": int(to_date.timestamp()),
                "tf": tf
            }
            
            response = requests.get(url, params=params, headers=self._get_headers(), timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data:
                    df = pd.DataFrame(data['data'])
                    # Переименовываем колонки
                    if 'time' in df.columns:
                        df['time'] = pd.to_datetime(df['time'], unit='ms')
                    df = df.rename(columns={
                        'open': 'open',
                        'high': 'high',
                        'low': 'low',
                        'close': 'close',
                        'volume': 'volume'
                    })
                    df = df[['time', 'open', 'high', 'low', 'close', 'volume']]
                    df = df.sort_values('time').reset_index(drop=True)
                    return df
            
        except Exception as e:
            self.logger.error(f"Ошибка загрузки свечей Alor для {ticker}: {e}")
        
        return pd.DataFrame()

