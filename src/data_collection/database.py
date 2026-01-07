"""Работа с базой данных (SQLAlchemy ORM)"""

from datetime import datetime
from typing import Optional
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging

Base = declarative_base()
logger = logging.getLogger(__name__)


class Candle(Base):
    """Таблица свечей"""
    __tablename__ = 'candles'
    
    id = Column(Integer, primary_key=True)
    ticker = Column(String(10), index=True, nullable=False)
    timeframe = Column(String(5), nullable=False)  # '1m', '1h', '1d'
    time = Column(DateTime, index=True, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)


class Trade(Base):
    """Таблица исполненных сделок"""
    __tablename__ = 'trades'
    
    id = Column(Integer, primary_key=True)
    order_id = Column(String(50), unique=True)
    ticker = Column(String(10), nullable=False)
    direction = Column(String(4), nullable=False)  # 'BUY' or 'SELL'
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    commission = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.utcnow)
    strategy = Column(String(50))  # Какая стратегия сделала сделку


class PortfolioSnapshot(Base):
    """Снимки портфеля для отслеживания динамики"""
    __tablename__ = 'portfolio_snapshots'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    total_value = Column(Float, nullable=False)
    cash = Column(Float, nullable=False)
    positions_json = Column(String)  # JSON со всеми позициями


class DatabaseManager:
    """Менеджер для работы с БД"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        try:
            self.engine = create_engine(database_url, echo=False)
            Base.metadata.create_all(self.engine)
            self.Session = sessionmaker(bind=self.engine)
            logger.info(f"Подключение к БД установлено: {database_url.split('@')[1] if '@' in database_url else 'локальная'}")
        except Exception as e:
            logger.error(f"Ошибка подключения к БД: {e}")
            raise
    
    def save_candles(self, df: pd.DataFrame, ticker: str, timeframe: str) -> None:
        """Сохранить свечи в БД"""
        if df.empty:
            return
        
        session = self.Session()
        try:
            for _, row in df.iterrows():
                candle = Candle(
                    ticker=ticker,
                    timeframe=timeframe,
                    time=row.get('time', row.get('timestamp', datetime.now())),
                    open=row['open'],
                    high=row['high'],
                    low=row['low'],
                    close=row['close'],
                    volume=int(row.get('volume', 0))
                )
                session.merge(candle)
            session.commit()
            logger.info(f"Сохранено {len(df)} свечей для {ticker}")
        except Exception as e:
            session.rollback()
            logger.error(f"Ошибка сохранения свечей: {e}")
            raise
        finally:
            session.close()
    
    def load_candles(
        self,
        ticker: str,
        timeframe: str,
        start_date: datetime,
        end_date: datetime,
    ) -> pd.DataFrame:
        """Загрузить свечи из БД"""
        session = self.Session()
        try:
            query = (
                session.query(Candle)
                .filter(
                    Candle.ticker == ticker,
                    Candle.timeframe == timeframe,
                    Candle.time >= start_date,
                    Candle.time <= end_date
                )
                .order_by(Candle.time)
            )
            
            df = pd.read_sql(query.statement, session.bind)
            if not df.empty and 'time' in df.columns:
                df['time'] = pd.to_datetime(df['time'])
            return df
        except Exception as e:
            logger.error(f"Ошибка загрузки свечей: {e}")
            return pd.DataFrame()
        finally:
            session.close()
    
    def save_trade(self, trade_data: dict) -> None:
        """Сохранить сделку"""
        session = self.Session()
        try:
            trade = Trade(**trade_data)
            session.add(trade)
            session.commit()
            logger.info(f"Сделка сохранена: {trade_data.get('ticker')} {trade_data.get('direction')}")
        except Exception as e:
            session.rollback()
            logger.error(f"Ошибка сохранения сделки: {e}")
            raise
        finally:
            session.close()
