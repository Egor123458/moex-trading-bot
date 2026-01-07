#!/usr/bin/env python3
"""Тест модуля сбора данных"""

import sys
from pathlib import Path

# Добавляем корневую папку в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

from datetime import datetime, timedelta
from src.data_collection.moex_api import MOEXDataCollector
from src.data_collection.data_cleaner import DataCleaner
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    print("="*60)
    print("ТЕСТ МОДУЛЯ СБОРА ДАННЫХ MOEX")
    print("="*60)
    
    # Инициализация
    collector = MOEXDataCollector()
    cleaner = DataCleaner()
    
    # Проверка подключения
    print("\n1. Проверка подключения к MOEX API...")
    if not collector.test_connection():
        print("✗ Не удалось подключиться к MOEX API")
        return
    print("✓ Подключение успешно")
    
    # Загрузка данных
    print("\n2. Загрузка исторических данных (SBER, последние 60 дней)...")
    data = collector.get_historical_candles(
        ticker='SBER',
        start_date=datetime.now() - timedelta(days=60),
        end_date=datetime.now(),
        timeframe='1h'
    )
    
    if data.empty:
        print("✗ Не удалось загрузить данные")
        return
    
    print(f"✓ Загружено {len(data)} свечей")
    print(f"\nПервые 3 строки:")
    print(data.head(3))
    
    # Очистка данных
    print("\n3. Очистка данных...")
    cleaned_data = cleaner.clean_ohlcv(data)
    print(f"✓ После очистки: {len(cleaned_data)} строк")
    
    # Статистика
    print("\n4. Статистика:")
    print(f"Период: {cleaned_data['time'].min()} — {cleaned_data['time'].max()}")
    print(f"Цена: мин={cleaned_data['close'].min():.2f}, макс={cleaned_data['close'].max():.2f}")
    print(f"Средний объем: {cleaned_data['volume'].mean():.0f}")
    
    # Текущая цена
    print("\n5. Текущая цена...")
    current_price = collector.get_latest_price('SBER')
    if current_price:
        print(f"✓ SBER: {current_price:.2f} ₽")
    
    print("\n" + "="*60)
    print("ТЕСТ ЗАВЕРШЕН УСПЕШНО!")
    print("="*60)

if __name__ == "__main__":
    main()
