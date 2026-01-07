"""Непрерывное обучение модели 24/7"""

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
import json
import schedule
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/training.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class ContinuousTrainer:
    """Система непрерывного обучения моделей"""
    
    def __init__(self):
        self.db = DatabaseManager(settings.db.DATABASE_URL)
        self.feature_eng = FeatureEngineer()
        self.best_models = {}
        self.training_history = []
        
        logger.info("="*60)
        logger.info("CONTINUOUS TRAINER ИНИЦИАЛИЗИРОВАН")
        logger.info("="*60)
    
    def train_models_hourly(self):
        """Ежечасное обучение моделей"""
        logger.info(f"\n[{datetime.now()}] Начало ежечасного обучения...")
        
        try:
            # Загрузка данных
            tickers = ['SBER', 'GAZP', 'LKOH', 'GMKN']
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            
            all_features = []
            all_labels_dict = {5: [], 10: [], 15: []}
            
            for ticker in tickers:
                data = self.db.load_candles(ticker, '1h', start_date, end_date)
                
                if data.empty:
                    continue
                
                features = self.feature_eng.create_features(data)
                
                if len(features) > 0:
                    for t in tickers:
                        features[f'is_{t}'] = int(ticker == t)
                    
                    all_features.append(features)
                    
                    # Создание labels
                    if 'time' in data.columns:
                        data = data.set_index('time')
                    
                    for horizon in [5, 10, 15]:
                        future_returns = data['close'].shift(-horizon) / data['close'] - 1
                        labels = (future_returns > 0.015).astype(int)
                        all_labels_dict[horizon].append(labels)
            
            X_combined = pd.concat(all_features, axis=0, ignore_index=False)
            
            # Обучение для каждого горизонта
            best_auc = 0
            best_horizon = 5
            
            for horizon in [5, 10, 15]:
                y_combined = pd.concat(all_labels_dict[horizon], axis=0, ignore_index=False)
                
                valid_indices = X_combined.index.intersection(y_combined.index)
                X = X_combined.loc[valid_indices]
                y = y_combined.loc[valid_indices]
                
                if len(X) < 100:
                    continue
                
                # Параметры с улучшениями
                scale_pos_weight = (len(y) - y.sum()) / y.sum() if y.sum() > 0 else 1.0
                
                params = {
                    'objective': 'binary:logistic',
                    'eval_metric': 'auc',
                    'max_depth': 5,  # Увеличено для лучшей точности
                    'learning_rate': 0.02,
                    'n_estimators': 800,  # Больше деревьев
                    'subsample': 0.8,
                    'colsample_bytree': 0.8,
                    'colsample_bylevel': 0.8,
                    'min_child_weight': 3,
                    'gamma': 0.1,
                    'reg_alpha': 0.1,
                    'reg_lambda': 1.0,
                    'scale_pos_weight': scale_pos_weight,
                    'random_state': 42
                }
                
                model = XGBoostClassifier(params=params)
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
                
                # Сохраняем модель
                model_path = f'data/models/CONTINUOUS_xgboost_1h_h{horizon}.pkl'
                model.save(model_path)
                
                # Сохраняем метрики
                info_path = f'data/models/CONTINUOUS_xgboost_1h_h{horizon}_info.json'
                with open(info_path, 'w') as f:
                    json.dump({
                        'roc_auc': float(auc),
                        'optimal_threshold': float(best_threshold),
                        'horizon': horizon,
                        'timestamp': datetime.now().isoformat()
                    }, f, indent=2)
                
                logger.info(f"  Horizon {horizon}: ROC-AUC = {auc:.4f}")
                
                if auc > best_auc:
                    best_auc = auc
                    best_horizon = horizon
                    
                    # Копируем лучшую модель
                    best_model_path = 'data/models/MULTI_xgboost_1h_BEST.pkl'
                    model.save(best_model_path)
                    logger.info(f"  ✓ Новая лучшая модель! AUC={auc:.4f}")
            
            # Логируем результаты
            self.training_history.append({
                'timestamp': datetime.now().isoformat(),
                'best_auc': best_auc,
                'best_horizon': best_horizon
            })
            
            logger.info(f"✓ Ежечасное обучение завершено (Best AUC: {best_auc:.4f})")
        
        except Exception as e:
            logger.error(f"Ошибка при обучении: {e}")
            import traceback
            traceback.print_exc()
    
    def run_scheduler(self):
        """Запуск планировщика"""
        # Обучение каждый час
        schedule.every().hour.do(self.train_models_hourly)
        
        logger.info("\n" + "="*60)
        logger.info("ПЛАНИРОВЩИК ЗАПУЩЕН")
        logger.info("Обучение каждый час")
        logger.info("="*60 + "\n")
        
        # Главный цикл
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Проверка каждую минуту
            except KeyboardInterrupt:
                logger.info("\nПланировщик остановлен")
                break
            except Exception as e:
                logger.error(f"Ошибка в планировщике: {e}")
                time.sleep(300)  # Ждем 5 минут перед повтором


if __name__ == "__main__":
    trainer = ContinuousTrainer()
    trainer.run_scheduler()
