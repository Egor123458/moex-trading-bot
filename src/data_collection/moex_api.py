"""
Клиент для работы с MOEX API
Использует библиотеку moexalgo для получения данных
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import pandas as pd

try:
    import moexalgo
    MOEX_AVAILABLE = True
except ImportError:
    MOEX_AVAILABLE = False
    moexalgo = None

logger = logging.getLogger(__name__)


class MOEXDataCollector:
    """Коллектор данных с MOEX через moexalgo"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Инициализация коллектора
        
        Args:
            api_key: API ключ MOEX (опционально, для некоторых методов)
        """
        if not MOEX_AVAILABLE:
            logger.warning("moexalgo не установлен! Установите: pip install moexalgo")
        
        self.api_key = api_key
        self.logger = logging.getLogger(__name__)
        
        if MOEX_AVAILABLE:
            self.logger.info("MOEXDataCollector инициализирован")
        else:
            self.logger.warning("MOEXDataCollector инициализирован без moexalgo")
    
    def test_connection(self) -> bool:
        """
        Проверка подключения к MOEX API
        
        Returns:
            True если подключение успешно
        """
        if not MOEX_AVAILABLE:
            return False
        
        try:
            # Пробуем получить список тикеров
            tickers = self.get_ticker_list(limit=1)
            return len(tickers) > 0
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
        if not MOEX_AVAILABLE:
            self.logger.error("moexalgo не установлен!")
            return pd.DataFrame()
        
        try:
            self.logger.info(f"Загрузка свечей {ticker} ({timeframe}) с {start_date.date()} по {end_date.date()}")
            
            # Маппинг таймфреймов для moexalgo
            timeframe_map = {
                '1m': '1min',
                '5m': '5min',
                '15m': '15min',
                '1h': '1hour',
                '1d': '1day'
            }
            
            moex_timeframe = timeframe_map.get(timeframe, '1hour')
            
            # Используем moexalgo для получения данных
            from moexalgo import Market, Candle
            
            # Получаем данные через Candle
            data = Candle(
                ticker=ticker,
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d'),
                board='TQBR',  # Торговая площадка
                market='shares'  # Рынок акций
            )
            
            # Конвертируем в DataFrame
            df = pd.DataFrame(data)
            
            if df.empty:
                self.logger.warning(f"Нет данных для {ticker}")
                return pd.DataFrame()
            
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
            
            # Сортируем по времени
            df = df.sort_values('time').reset_index(drop=True)
            
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
        if not MOEX_AVAILABLE:
            self.logger.error("moexalgo не установлен!")
            return None
        
        try:
            from moexalgo import Market
            
            # Получаем стакан через Market
            market = Market('shares')
            orderbook = market.orderbook(ticker, board='TQBR')
            
            return orderbook
            
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
        if not MOEX_AVAILABLE:
            self.logger.error("moexalgo не установлен!")
            return []
        
        try:
            from moexalgo import Market
            
            # Получаем список инструментов
            market = Market('shares')
            instruments = market.tradestats()
            
            # Извлекаем тикеры
            tickers = []
            if hasattr(instruments, 'secid'):
                tickers = list(instruments['secid'].unique())
            elif isinstance(instruments, pd.DataFrame) and 'secid' in instruments.columns:
                tickers = instruments['secid'].unique().tolist()
            elif isinstance(instruments, list):
                tickers = [item.get('secid', '') for item in instruments if isinstance(item, dict)]
            
            # Фильтруем пустые значения
            tickers = [t for t in tickers if t and isinstance(t, str)]
            
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
        if not MOEX_AVAILABLE:
            return None
        
        try:
            from moexalgo import Market
            
            market = Market('shares')
            trades = market.tradestats(ticker, board='TQBR')
            
            if isinstance(trades, pd.DataFrame) and not trades.empty:
                # Берем последнюю цену
                return float(trades.iloc[-1]['pr_close']) if 'pr_close' in trades.columns else None
            elif isinstance(trades, dict):
                return trades.get('pr_close')
            
            return None
            
        except Exception as e:
            self.logger.error(f"Ошибка получения цены для {ticker}: {e}")
            return None
