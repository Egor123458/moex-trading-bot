"""
Интеграция с Finam Trade API
Документация: https://www.finam.ru/profile/moex-aktsii/sber/export/
"""

import logging
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict
import time

from src.brokers.base_broker import BaseBroker

logger = logging.getLogger(__name__)


class FinamBroker(BaseBroker):
    """Клиент для Finam Trade API"""
    
    def __init__(self, token: str = "", account_id: str = "", sandbox: bool = False):
        """
        Args:
            token: API токен Finam (не требуется для исторических данных)
            account_id: ID счета (для торговли)
            sandbox: Режим песочницы (Finam не поддерживает sandbox)
        """
        super().__init__(token, account_id, sandbox)
        self.base_url = "https://trade-api.finam.ru" if token else "https://export.finam.ru"
        self.logger.info(f"FinamBroker инициализирован (sandbox={sandbox})")
    
    def get_portfolio(self) -> Dict:
        """Получить текущий портфель"""
        if not self.token:
            self.logger.warning("Токен Finam не указан, возвращаем пустой портфель")
            return {"positions": [], "total_value": 0.0, "cash": 0.0}
        
        try:
            # Finam Trade API - пробуем разные варианты URL
            # Примечание: Finam может использовать другой формат API или требовать специальной авторизации
            
            # Вариант 1: Стандартный REST API
            base_url = "https://trade-api.finam.ru"
            url = f"{base_url}/api/v1/portfolio"
            
            headers = {
                "X-Api-Key": self.token,
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            params = {}
            if self.account_id:
                params['accountId'] = self.account_id
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            self.logger.debug(f"Finam API запрос: url={url}, status={response.status_code}")
            
            # Проверяем, что ответ JSON, а не HTML
            content_type = response.headers.get('Content-Type', '')
            if 'text/html' in content_type:
                self.logger.warning(f"Finam API вернул HTML вместо JSON. URL может быть неправильным.")
                self.logger.warning(f"Попробуйте проверить документацию Finam API или использовать другой endpoint.")
                # Возвращаем пустой портфель, но не падаем
                return {"positions": [], "total_value": 0.0, "cash": 0.0}
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    self.logger.debug(f"Finam API данные: {data}")
                    
                    positions = []
                    total_value = 0.0
                    cash = 0.0
                    
                    # Парсинг ответа Finam (разные возможные структуры)
                    # Вариант 1: positions в корне
                    if 'positions' in data:
                        for pos in data['positions']:
                            pos_value = pos.get('value', 0.0)
                            if isinstance(pos_value, dict):
                                pos_value = pos_value.get('value', 0.0) or pos_value.get('amount', 0.0)
                            
                            positions.append({
                                "ticker": pos.get('ticker', pos.get('symbol', '')),
                                "quantity": pos.get('quantity', pos.get('qty', 0)),
                                "current_price": pos.get('price', pos.get('currentPrice', 0.0)),
                                "average_buy_price": pos.get('average_price', pos.get('averagePrice', 0.0)),
                            })
                            total_value += float(pos_value) if pos_value else 0.0
                    
                    # Вариант 2: data.positions
                    elif 'data' in data and 'positions' in data['data']:
                        for pos in data['data']['positions']:
                            pos_value = pos.get('value', 0.0)
                            if isinstance(pos_value, dict):
                                pos_value = pos_value.get('value', 0.0) or pos_value.get('amount', 0.0)
                            
                            positions.append({
                                "ticker": pos.get('ticker', pos.get('symbol', '')),
                                "quantity": pos.get('quantity', pos.get('qty', 0)),
                                "current_price": pos.get('price', pos.get('currentPrice', 0.0)),
                                "average_buy_price": pos.get('average_price', pos.get('averagePrice', 0.0)),
                            })
                            total_value += float(pos_value) if pos_value else 0.0
                    
                    # Получение cash
                    cash = data.get('cash', data.get('availableCash', 0.0))
                    if isinstance(cash, dict):
                        cash = cash.get('value', cash.get('amount', 0.0))
                    
                    # Если total_value не найден, пытаемся вычислить из позиций или взять из data
                    if total_value == 0.0:
                        total_value = data.get('totalValue', data.get('totalAmount', 0.0))
                        if isinstance(total_value, dict):
                            total_value = total_value.get('value', total_value.get('amount', 0.0))
                    
                    self.logger.info(f"Портфель Finam: позиций={len(positions)}, total_value={total_value}, cash={cash}")
                    
                    return {
                        "positions": positions,
                        "total_value": float(total_value) if total_value else 0.0,
                        "cash": float(cash) if cash else 0.0
                    }
                except ValueError as e:
                    self.logger.error(f"Ошибка парсинга JSON от Finam API: {e}")
                    self.logger.debug(f"Ответ API: {response.text[:500]}")
            else:
                self.logger.warning(f"Finam API вернул статус {response.status_code}: {response.text[:200]}")
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Ошибка запроса к Finam API: {e}")
        except Exception as e:
            self.logger.error(f"Ошибка получения портфеля Finam: {e}", exc_info=True)
        
        # Возвращаем пустой портфель, но бот продолжит работу
        # Баланс будет использоваться из INITIAL_CAPITAL в настройках
        self.logger.warning("Не удалось получить портфель из Finam API. Используется INITIAL_CAPITAL из настроек.")
        return {"positions": [], "total_value": 0.0, "cash": 0.0}
    
    def place_market_order(
        self,
        ticker: str,
        quantity: int,
        direction: str
    ) -> Dict:
        """Разместить рыночный ордер"""
        if not self.token:
            self.logger.error("Токен Finam не указан!")
            return {"order_id": "", "status": "FAILED", "lots_executed": 0, "executed_price": 0.0}
        
        try:
            url = f"{self.base_url}/api/v1/orders"
            headers = {"X-Api-Key": self.token}
            data = {
                "ticker": ticker,
                "quantity": quantity,
                "operation": "Buy" if direction.upper() == "BUY" else "Sell",
                "orderType": "Market"
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
            self.logger.error(f"Ошибка размещения ордера Finam: {e}")
        
        return {"order_id": "", "status": "FAILED", "lots_executed": 0, "executed_price": 0.0}
    
    def get_figi_by_ticker(self, ticker: str) -> Optional[str]:
        """Получить FIGI по тикеру (для Finam используется сам тикер)"""
        # Finam использует тикеры напрямую, FIGI не требуется
        return ticker
    
    def get_candles(
        self,
        ticker: str,
        from_date: datetime,
        to_date: datetime,
        interval: str = '1h'
    ) -> pd.DataFrame:
        """Получить исторические свечи через Finam Export API"""
        try:
            # Finam Export API (не требует токена)
            # Формат: https://export.finam.ru/export9.out?market=1&em=3&code=SBER&apply=0&df=1&mf=0&yf=2024&from=01.01.2024&dt=31&mt=11&yt=2024&to=31.12.2024&p=8&f=SBER_240101_241231&e=.csv&cn=SBER&dtf=1&tmf=1&MSOR=1&mstime=on&mstimever=1&sep=1&sep2=1&datf=1&at=1
            
            # Маппинг таймфреймов для Finam
            timeframe_map = {
                '1m': 1,
                '5m': 2,
                '15m': 3,
                '1h': 4,
                '1d': 5
            }
            
            period = timeframe_map.get(interval, 4)
            
            # Формируем URL для экспорта
            url = "https://export.finam.ru/export9.out"
            params = {
                'market': 1,  # Фондовый рынок
                'em': self._get_finam_code(ticker),  # Код инструмента
                'code': ticker,
                'apply': 0,
                'df': from_date.day,
                'mf': from_date.month - 1,
                'yf': from_date.year,
                'from': from_date.strftime('%d.%m.%Y'),
                'dt': to_date.day,
                'mt': to_date.month - 1,
                'yt': to_date.year,
                'to': to_date.strftime('%d.%m.%Y'),
                'p': period,
                'f': f"{ticker}_{from_date.strftime('%y%m%d')}_{to_date.strftime('%y%m%d')}",
                'e': '.csv',
                'cn': ticker,
                'dtf': 1,
                'tmf': 1,
                'MSOR': 1,
                'mstime': 'on',
                'mstimever': 1,
                'sep': 1,
                'sep2': 1,
                'datf': 1,
                'at': 1
            }
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                # Парсим CSV
                from io import StringIO
                df = pd.read_csv(StringIO(response.text), sep=';')
                
                # Переименовываем колонки
                if len(df.columns) >= 7:
                    df.columns = ['date', 'time', 'open', 'high', 'low', 'close', 'volume']
                    df['time'] = pd.to_datetime(df['date'] + ' ' + df['time'])
                    df = df.rename(columns={'time': 'time'})
                    df = df[['time', 'open', 'high', 'low', 'close', 'volume']]
                    df = df.sort_values('time').reset_index(drop=True)
                    return df
            
        except Exception as e:
            self.logger.error(f"Ошибка загрузки свечей Finam для {ticker}: {e}")
        
        return pd.DataFrame()
    
    def _get_finam_code(self, ticker: str) -> int:
        """Получить код инструмента в Finam (упрощенная версия)"""
        # Для основных тикеров MOEX
        codes = {
            'SBER': 3,
            'GAZP': 16842,
            'LKOH': 8,
            'GMKN': 175924,
            'YNDX': 388383,
            'NVTK': 17370,
            'PLZL': 17137,
            'TATN': 20,
            'ROSN': 17273,
            'MGNT': 17086
        }
        return codes.get(ticker, 3)  # По умолчанию SBER


