#!/usr/bin/env python3
"""Скрипт для загрузки исторических данных с MOEX в БД"""

import sys
from pathlib import Path

# Добавляем корневую папку в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_collection.moex_api import MOEXDataCollector
from src.data_collection.data_cleaner import DataCleaner
from src.data_collection.database import DatabaseManager
from config.settings import settings
from datetime import datetime, timedelta
import yaml
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    print("="*60)
    print("ЗАГРУЗКА ИСТОРИЧЕСКИХ ДАННЫХ С MOEX")
    print("="*60)
    
    # Загрузка конфига
    with open('config/trading_config.yaml') as f:
        config = yaml.safe_load(f)
    
    tickers = config['tickers']['primary']
    
    # Инициализация
    collector = MOEXDataCollector()
    cleaner = DataCleaner()
    db = DatabaseManager(settings.db.DATABASE_URL)
    
    # Параметры загрузки
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)  # 1 год истории
    timeframe = '1h'  # Часовые свечи
    
    print(f"\nПараметры:")
    print(f"Период: {start_date.date()} — {end_date.date()}")
    print(f"Таймфрейм: {timeframe}")
    print(f"Тикеры: {', '.join(tickers)}")
    print()
    
    # Загрузка для каждого тикера
    for i, ticker in enumerate(tickers, 1):
        print(f"\n[{i}/{len(tickers)}] Обработка {ticker}...")
        
        try:
            # Загрузка с MOEX
            candles = collector.get_historical_candles(
                ticker=ticker,
                start_date=start_date,
                end_date=end_date,
                timeframe=timeframe
            )
            
            if candles.empty:
                print(f"  ✗ Нет данных для {ticker}")
                continue
            
            # Очистка
            cleaned = cleaner.clean_ohlcv(candles)
            
            # Сохранение в БД
            db.save_candles(cleaned, ticker, timeframe)
            
            print(f"  ✓ {ticker}: {len(cleaned)} свечей сохранено")
            
        except Exception as e:
            print(f"  ✗ Ошибка для {ticker}: {e}")
            continue
    
    # Итоговая статистика
    print("\n" + "="*60)
    print("ЗАГРУЗКА ЗАВЕРШЕНА")
    print("="*60)
    
    stats = db.get_stats()
    print(f"\nСтатистика БД:")
    print(f"  Всего свечей: {stats['candles']}")
    print(f"  Тикеров: {len(stats['tickers'])}")
    print(f"  Список: {', '.join(stats['tickers'])}")

if __name__ == "__main__":
    main()
