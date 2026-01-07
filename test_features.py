#!/usr/bin/env python3
"""Тест создания признаков"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.data_collection.database import DatabaseManager
from src.ml_models.features.feature_engineering import FeatureEngineer
from config.settings import settings
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)

def main():
    print("="*60)
    print("ТЕСТ СОЗДАНИЯ ПРИЗНАКОВ ДЛЯ ML")
    print("="*60)
    
    # Загрузка данных из БД
    db = DatabaseManager(settings.db.DATABASE_URL)
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    
    print("\nЗагрузка данных SBER из БД...")
    data = db.load_candles('SBER', '1h', start_date, end_date)
    
    if data.empty:
        print("✗ Нет данных в БД")
        return
    
    print(f"✓ Загружено {len(data)} свечей")
    
    # Создание признаков
    print("\nСоздание признаков...")
    feature_eng = FeatureEngineer()
    features = feature_eng.create_features(data)
    
    print(f"\n✓ Создано {len(features.columns)} признаков")
    print(f"✓ Строк данных: {len(features)}")
    
    print("\nПервые признаки:")
    print(features[['close', 'returns', 'rsi', 'macd', 'bb_position']].head())
    
    # Создание labels
    print("\nСоздание целевой переменной (предсказание на 30 периодов вперед)...")
    labels = feature_eng.create_labels(data, horizon=30)
    
    print(f"✓ Распределение классов:")
    print(f"  Рост (1): {labels.sum()} ({labels.sum()/len(labels)*100:.1f}%)")
    print(f"  Падение (0): {len(labels) - labels.sum()} ({(len(labels)-labels.sum())/len(labels)*100:.1f}%)")
    
    print("\n" + "="*60)
    print("ТЕСТ ЗАВЕРШЕН!")
    print("="*60)

if __name__ == "__main__":
    main()
