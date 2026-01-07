"""
Клиент для работы с MOEX API
Использует прямой REST API MOEX (без зависимостей от moexalgo)
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import pandas as pd
import requests
import time

logger = logging.getLogger(__name__)


class MOEXDataCollector:
    """Коллектор данных с MOEX через REST API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Инициализация коллектора
        
        Args:
            api_key: API ключ MOEX (опционально, для некоторых методов)
        """
        self.api_key = api_key
        self.base_url = "https://iss.moex.com/iss"
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)
        self.logger.info("MOEXDataCollector инициализирован (REST API)")
    
    def test_connection(self) -> bool:
        """
        Проверка подключения к MOEX API
        
        Returns:
            True если подключение успешно
        """
        try:
            response = self.session.get(f"{self.base_url}/engines/stock/markets/shares/boards/TQBR/securities.json", timeout=10)
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Ошибка подключения к MOEX: {e}")
            return False
    
    def get_historical_candles(
        self,
        ticker: str,
        start_date: datetime,
        end_date: datetime,
        timeframe: str = '1h'
    ) -> pd.DataFrame:
        """
        Получить исторические свечи
        
        Args:
            ticker: Тикер акции (например, 'SBER')
            start_date: Начальная дата
            end_date: Конечная дата
            timeframe: Таймфрейм ('1m', '5m', '1h', '1d')
        
        Returns:
            DataFrame с колонками: time, open, high, low, close, volume
        """
        try:
            self.logger.info(f"Загрузка свечей {ticker} ({timeframe}) с {start_date.date()} по {end_date.date()}")
            
            # Маппинг таймфреймов для MOEX API
            timeframe_map = {
                '1m': 1,
                '5m': 5,
                '10m': 10,
                '15m': 15,
                '30m': 30,
                '1h': 60,
                '1d': 24
            }
            
            interval = timeframe_map.get(timeframe, 60)  # По умолчанию 1 час
            
            # Формируем URL для запроса свечей
            url = f"{self.base_url}/engines/stock/markets/shares/boards/TQBR/securities/{ticker}/candles.json"
            
            params = {
                'from': start_date.strftime('%Y-%m-%d'),
                'till': end_date.strftime('%Y-%m-%d'),
                'interval': interval
            }
            
            all_data = []
            start = start_date
            
            # MOEX API возвращает данные порциями, нужно делать несколько запросов
            while start < end_date:
                params['from'] = start.strftime('%Y-%m-%d')
                params['till'] = min(start + timedelta(days=100), end_date).strftime('%Y-%m-%d')
                
                response = self.session.get(url, params=params, timeout=30)
                
                if response.status_code != 200:
                    self.logger.warning(f"Ошибка запроса: {response.status_code}")
                    break
                
                data = response.json()
                
                if 'candles' not in data or 'data' not in data['candles']:
                    break
                
                columns = data['candles']['columns']
                rows = data['candles']['data']
                
                if not rows:
                    break
                
                # Конвертируем в DataFrame
                df_chunk = pd.DataFrame(rows, columns=columns)
                all_data.append(df_chunk)
                
                # Обновляем дату начала для следующего запроса
                last_date = pd.to_datetime(df_chunk.iloc[-1]['begin'])
                start = last_date + timedelta(days=1)
                
                # Защита от бесконечного цикла
                if len(all_data) > 50:
                    break
                
                time.sleep(0.1)  # Небольшая задержка между запросами
            
            if not all_data:
                self.logger.warning(f"Нет данных для {ticker}")
                return pd.DataFrame()
            
            # Объединяем все части
            df = pd.concat(all_data, ignore_index=True)
            
            # Переименовываем колонки в стандартный формат
            column_map = {
                'begin': 'time',
                'open': 'open',
                'high': 'high',
                'low': 'low',
                'close': 'close',
                'volume': 'volume'
            }
            
            # Приводим к стандартным названиям колонок
            df = df.rename(columns=column_map)
            
            # Оставляем только нужные колонки
            required_cols = ['time', 'open', 'high', 'low', 'close', 'volume']
            available_cols = [col for col in required_cols if col in df.columns]
            df = df[available_cols]
            
            # Убеждаемся, что time в формате datetime
            if 'time' in df.columns:
                df['time'] = pd.to_datetime(df['time'])
            
            # Сортируем по времени и удаляем дубликаты
            df = df.sort_values('time').drop_duplicates(subset=['time']).reset_index(drop=True)
            
            # Фильтруем по датам
            df = df[(df['time'] >= start_date) & (df['time'] <= end_date)]
            
            self.logger.info(f"Загружено {len(df)} свечей для {ticker}")
            return df
            
        except Exception as e:
            self.logger.error(f"Ошибка загрузки свечей для {ticker}: {e}")
            return pd.DataFrame()
    
    def get_orderbook(self, ticker: str) -> Optional[Dict]:
        """
        Получить текущий стакан заявок
        
        Args:
            ticker: Тикер акции
        
        Returns:
            Dict с данными стакана или None
        """
        try:
            url = f"{self.base_url}/engines/stock/markets/shares/boards/TQBR/securities/{ticker}/orderbook.json"
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            if 'orderbook' not in data:
                return None
            
            columns = data['orderbook']['columns']
            rows = data['orderbook']['data']
            
            if not rows:
                return None
            
            # Конвертируем в DataFrame для удобства
            df = pd.DataFrame(rows, columns=columns)
            
            return {
                'bids': df[df['buy_sell'] == 'B'].to_dict('records') if 'buy_sell' in df.columns else [],
                'asks': df[df['buy_sell'] == 'S'].to_dict('records') if 'buy_sell' in df.columns else []
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка получения стакана для {ticker}: {e}")
            return None
    
    def get_ticker_list(self, limit: Optional[int] = None) -> List[str]:
        """
        Получить список доступных тикеров
        
        Args:
            limit: Максимальное количество тикеров (None = все)
        
        Returns:
            List тикеров
        """
        try:
            url = f"{self.base_url}/engines/stock/markets/shares/boards/TQBR/securities.json"
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                self.logger.warning("Не удалось получить список тикеров, используем fallback")
                return ['SBER', 'GAZP', 'LKOH', 'YNDX', 'GMKN', 'NVTK', 'PLZL', 'TATN', 'ROSN', 'MGNT']
            
            data = response.json()
            
            if 'securities' not in data or 'data' not in data['securities']:
                return ['SBER', 'GAZP', 'LKOH', 'YNDX', 'GMKN', 'NVTK', 'PLZL', 'TATN', 'ROSN', 'MGNT']
            
            columns = data['securities']['columns']
            rows = data['securities']['data']
            
            # Извлекаем тикеры (колонка SECID)
            secid_idx = columns.index('SECID') if 'SECID' in columns else None
            
            if secid_idx is None:
                return ['SBER', 'GAZP', 'LKOH', 'YNDX', 'GMKN', 'NVTK', 'PLZL', 'TATN', 'ROSN', 'MGNT']
            
            tickers = [row[secid_idx] for row in rows if row[secid_idx]]
            
            if limit:
                tickers = tickers[:limit]
            
            self.logger.info(f"Получено {len(tickers)} тикеров")
            return tickers
            
        except Exception as e:
            self.logger.error(f"Ошибка получения списка тикеров: {e}")
            # Возвращаем популярные тикеры как fallback
            return ['SBER', 'GAZP', 'LKOH', 'YNDX', 'GMKN', 'NVTK', 'PLZL', 'TATN', 'ROSN', 'MGNT']
    
    def get_current_price(self, ticker: str) -> Optional[float]:
        """
        Получить текущую цену тикера
        
        Args:
            ticker: Тикер акции
        
        Returns:
            Текущая цена или None
        """
        try:
            url = f"{self.base_url}/engines/stock/markets/shares/boards/TQBR/securities/{ticker}.json"
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            if 'marketdata' not in data or 'data' not in data['marketdata']:
                return None
            
            columns = data['marketdata']['columns']
            rows = data['marketdata']['data']
            
            if not rows:
                return None
            
            # Ищем колонку LAST (последняя цена сделки)
            last_idx = columns.index('LAST') if 'LAST' in columns else None
            
            if last_idx is not None:
                price = rows[0][last_idx]
                if price:
                    return float(price)
            
            # Если LAST нет, пробуем CLOSE
            close_idx = columns.index('CLOSE') if 'CLOSE' in columns else None
            if close_idx is not None:
                price = rows[0][close_idx]
                if price:
                    return float(price)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Ошибка получения цены для {ticker}: {e}")
            return None
