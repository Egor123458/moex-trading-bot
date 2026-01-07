#!/usr/bin/env python3
"""Максимально улучшенный скрипт обучения ML-модели"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_collection.database import DatabaseManager
from src.ml_models.features.feature_engineering import FeatureEngineer
from src.ml_models.models.xgboost_model import XGBoostClassifier
from config.settings import settings
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def train_optimized_model():
    """Обучить оптимизированную модель"""
    
    print("="*60)
    print("МАКСИМАЛЬНО ОПТИМИЗИРОВАННОЕ ОБУЧЕНИЕ")
    print("="*60)
    
    tickers = ['SBER', 'GAZP', 'LKOH', 'GMKN']
    timeframe = '1h'
    
    horizons = [5, 10, 15]
    threshold = 0.015
    
    print(f"\nТикеры: {tickers}")
    print(f"Таймфрейм: {timeframe}")
    print(f"Горизонты: {horizons}")
    print(f"Порог роста: {threshold*100:.1f}%")
    
    print("\n1. Загрузка данных из БД...")
    db = DatabaseManager(settings.db.DATABASE_URL)
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    # Словарь для хранения данных по каждому тикеру
    ticker_data = {}
    
    feature_eng = FeatureEngineer()
    
    for ticker in tickers:
        print(f"\n  Обработка {ticker}...")
        data = db.load_candles(ticker, timeframe, start_date, end_date)
        
        if data.empty:
            print(f"    ✗ Нет данных для {ticker}")
            continue
        
        print(f"    Загружено {len(data)} свечей")
        
        # Создание признаков
        features = feature_eng.create_features(data)
        
        if len(features) > 0:
            # Добавляем признак тикера
            for t in tickers:
                features[f'is_{t}'] = int(ticker == t)
            
            # Сохраняем признаки и исходные данные
            ticker_data[ticker] = {
                'features': features,
                'data': data
            }
            
            print(f"    ✓ Создано {len(features.columns)} признаков, {len(features)} строк")
    
    best_model = None
    best_auc = 0
    best_horizon = 0
    
    # Обучение для каждого горизонта
    for horizon in horizons:
        print("\n" + "="*60)
        print(f"ГОРИЗОНТ: {horizon} периодов (~{horizon} часов)")
        print(f"Цель: предсказать рост >{threshold*100:.1f}%")
        print("="*60)
        
        all_X = []
        all_y = []
        
        # Для каждого тикера создаем labels с учетом его индексов
        for ticker, data_dict in ticker_data.items():
            features = data_dict['features']
            raw_data = data_dict['data']
            
            # Устанавливаем time как индекс для labels
            if 'time' in raw_data.columns:
                raw_data = raw_data.set_index('time')
            
            # Создаем labels на основе исходных данных
            future_returns = raw_data['close'].shift(-horizon) / raw_data['close'] - 1
            labels = (future_returns > threshold).astype(int)
            
            # Выравниваем по индексам features (которые уже отфильтрованы от NaN)
            common_idx = features.index.intersection(labels.index)
            
            X_ticker = features.loc[common_idx]
            y_ticker = labels.loc[common_idx]
            
            # Удаляем NaN из labels (из-за shift)
            valid_mask = ~y_ticker.isna()
            X_ticker = X_ticker[valid_mask]
            y_ticker = y_ticker[valid_mask]
            
            all_X.append(X_ticker)
            all_y.append(y_ticker)
        
        # Объединяем все данные
        X = pd.concat(all_X, axis=0)
        y = pd.concat(all_y, axis=0)
        
        print(f"\nПодготовлено {len(X)} сэмплов")
        print(f"Распределение:")
        print(f"  Сильный рост (>{threshold*100:.1f}%): {y.sum()} ({y.sum()/len(y)*100:.1f}%)")
        print(f"  Остальное: {len(y)-y.sum()} ({(len(y)-y.sum())/len(y)*100:.1f}%)")
        
        if y.sum() < len(y) * 0.2:
            print(f"\n⚠️ Дисбаланс классов! Используем scale_pos_weight")
            scale_pos_weight = (len(y) - y.sum()) / y.sum()
        else:
            scale_pos_weight = 1.0
        
        params = {
            'objective': 'binary:logistic',
            'eval_metric': 'auc',
            'max_depth': 4,
            'learning_rate': 0.03,
            'n_estimators': 500,
            'subsample': 0.7,
            'colsample_bytree': 0.7,
            'colsample_bylevel': 0.7,
            'min_child_weight': 5,
            'gamma': 0.2,
            'reg_alpha': 0.2,
            'reg_lambda': 2.0,
            'scale_pos_weight': scale_pos_weight,
            'random_state': 42
        }
        
        model = XGBoostClassifier(params=params)
        
        print("\n3. Обучение модели...")
        print("-"*60)
        model.train(X, y, test_size=0.2)
        
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import roc_auc_score, precision_recall_curve
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
        y_pred_proba = model.predict_proba(X_test)[:, 1]
        auc = roc_auc_score(y_test, y_pred_proba)
        
        precision, recall, thresholds = precision_recall_curve(y_test, y_pred_proba)
        f1_scores = 2 * (precision * recall) / (precision + recall + 1e-10)
        best_threshold_idx = np.argmax(f1_scores)
        best_threshold = thresholds[best_threshold_idx] if best_threshold_idx < len(thresholds) else 0.5
        
        print(f"\n📊 ROC-AUC: {auc:.4f}")
        print(f"📊 Оптимальный порог: {best_threshold:.3f}")
        
        if auc > best_auc:
            best_auc = auc
            best_model = model
            best_horizon = horizon
            print(f"\n✓ Это лучшая модель!")
        
        model_path = f'data/models/MULTI_xgboost_{timeframe}_h{horizon}_t{int(threshold*1000)}.pkl'
        Path('data/models').mkdir(parents=True, exist_ok=True)
        model.save(model_path)
        print(f"\n✓ Модель сохранена: {model_path}")
        
        import json
        threshold_info = {
            'optimal_threshold': float(best_threshold),
            'roc_auc': float(auc),
            'horizon': horizon,
            'growth_threshold': threshold
        }
        
        threshold_path = f'data/models/MULTI_xgboost_{timeframe}_h{horizon}_t{int(threshold*1000)}_info.json'
        with open(threshold_path, 'w') as f:
            json.dump(threshold_info, f, indent=2)
    
    print("\n" + "="*60)
    print("ИТОГОВЫЕ РЕЗУЛЬТАТЫ")
    print("="*60)
    print(f"Лучший горизонт: {best_horizon} периодов")
    print(f"Лучший ROC-AUC: {best_auc:.4f}")
    
    if best_auc > 0.55:
        print(f"\n✓✓✓ Результат ОТЛИЧНЫЙ! ROC-AUC > 0.55")
    elif best_auc > 0.52:
        print(f"\n✓✓ Результат ХОРОШИЙ. ROC-AUC между 0.52-0.55")
    elif best_auc > 0.50:
        print(f"\n✓ Результат ПРИЕМЛЕМЫЙ. ROC-AUC между 0.50-0.52")
    else:
        print(f"\n⚠️ Результат СЛАБЫЙ. ROC-AUC < 0.50")
    
    best_model_path = f'data/models/MULTI_xgboost_{timeframe}_BEST.pkl'
    best_model.save(best_model_path)
    print(f"\n✓ Лучшая модель: {best_model_path}")
    
    print("\n" + "="*60)
    print("ОБУЧЕНИЕ ЗАВЕРШЕНО!")
    print("="*60)

if __name__ == "__main__":
    train_optimized_model()
