"""Запуск бэктеста с автоматическим получением баланса"""

import sys
sys.path.append('.')

from src.backtesting.backtest_engine import BacktestEngine
from src.data_collection.database import DatabaseManager
from config.settings import settings
import pandas as pd
from datetime import datetime, timedelta
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Попытка получить баланс из Tinkoff API
initial_capital = None

try:
    token = os.getenv('TINKOFF_TOKEN', '').strip()
    
    if token and token != '':
        logger.info("="*60)
        logger.info("ПОЛУЧЕНИЕ БАЛАНСА ИЗ TINKOFF API")
        logger.info("="*60 + "\n")
        
        logger.info("Подключение к Tinkoff API...")
        
        from tinkoff_invest import TinkoffInvestApi
        
        # Создаем клиент API (sandbox режим)
        api = TinkoffInvestApi(token, sandbox=True)
        
        logger.info("Загрузка портфеля...")
        
        # Получаем портфель
        portfolio = api.get_portfolio()
        
        if portfolio:
            logger.info(f"✓ Портфель получен")
            
            # Ищем информацию о балансе
            if 'totalAmountPortfolio' in portfolio:
                total = portfolio['totalAmountPortfolio']
                
                # Может быть dict или число
                if isinstance(total, dict):
                    balance = float(total.get('value', 0))
                else:
                    balance = float(total)
                
                if balance > 0:
                    initial_capital = balance
                    logger.info(f"✓ Баланс: {initial_capital:,.0f} ₽\n")
        
except Exception as e:
    logger.warning(f"Ошибка API: {e}\n")

# Если не получилось - используем дефолт
if initial_capital is None or initial_capital <= 0:
    initial_capital = float(os.getenv('INITIAL_CAPITAL', '1000000'))
    logger.info("="*60)
    logger.info("ПОЛУЧЕНИЕ БАЛАНСА ИЗ КОНФИГА")
    logger.info("="*60)
    logger.info(f"⚠️  Используется капитал: {initial_capital:,.0f} ₽\n")

# Инициализация
db = DatabaseManager(settings.db.DATABASE_URL)
backtest = BacktestEngine(initial_capital=initial_capital)

# Загрузка данных
logger.info("="*60)
logger.info("ЗАГРУЗКА ИСТОРИЧЕСКИХ ДАННЫХ")
logger.info("="*60 + "\n")

tickers = ['SBER', 'GAZP', 'LKOH', 'GMKN']
end_date = datetime.now()
start_date = end_date - timedelta(days=180)

prices = {}
for ticker in tickers:
    logger.info(f"Загрузка данных для {ticker}...")
    df = db.load_candles(ticker, '1h', start_date, end_date)
    
    if df.empty:
        logger.warning(f"  Нет данных для {ticker}")
        continue
    
    # Переименовываем колонку времени
    if 'time' in df.columns:
        df = df.rename(columns={'time': 'timestamp'})
    elif 'begin' in df.columns:
        df = df.rename(columns={'begin': 'timestamp'})
    
    # Конвертируем в datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    prices[ticker] = df[['timestamp', 'close']].copy()
    logger.info(f"✓ Загружено {len(df)} свечей для {ticker}")

logger.info("")

if not prices:
    logger.error("Нет данных для бэктеста!")
    sys.exit(1)

# Генерация тестовых сигналов
logger.info("="*60)
logger.info("ГЕНЕРАЦИЯ ТЕСТОВЫХ СИГНАЛОВ")
logger.info("="*60 + "\n")

signals_data = []

# Сигнал 1: Покупка SBER
signals_data.append({
    'timestamp': start_date + timedelta(days=10), 
    'ticker': 'SBER', 
    'signal': 'BUY', 
    'probability': 0.7
})

# Сигнал 2: Продажа SBER
signals_data.append({
    'timestamp': start_date + timedelta(days=30), 
    'ticker': 'SBER', 
    'signal': 'SELL', 
    'probability': 0.6
})

# Сигнал 3: Покупка GAZP
signals_data.append({
    'timestamp': start_date + timedelta(days=15), 
    'ticker': 'GAZP', 
    'signal': 'BUY', 
    'probability': 0.65
})

# Сигнал 4: Продажа GAZP
signals_data.append({
    'timestamp': start_date + timedelta(days=40), 
    'ticker': 'GAZP', 
    'signal': 'SELL', 
    'probability': 0.55
})

signals = pd.DataFrame(signals_data)

logger.info(f"Создано {len(signals)} сигналов:\n")
print(signals.to_string(index=False))
print("")

# Запуск бэктеста
logger.info("="*60)
logger.info("ЗАПУСК БЭКТЕСТА")
logger.info("="*60 + "\n")

results = backtest.run_backtest(signals, prices)

# Результаты
if results:
    logger.info("\n" + "="*60)
    logger.info("📊 ИТОГОВЫЕ МЕТРИКИ")
    logger.info("="*60)
    logger.info(f"💰 Начальный капитал: {results['initial_capital']:,.0f} ₽")
    logger.info(f"💵 Конечная стоимость: {results['final_value']:,.0f} ₽")
    logger.info(f"📈 Доходность: {results['total_return_pct']:+.2f}%")
    logger.info(f"📉 Макс. просадка: {results['max_drawdown_pct']:.2f}%")
    logger.info(f"⚡ Sharpe Ratio: {results['sharpe_ratio']:.2f}")
    logger.info(f"🔄 Всего сделок: {results['total_trades']}")
    logger.info(f"🎯 Win Rate: {results['win_rate']*100:.1f}%")
    
    # Сохранение equity curve
    if 'equity_curve' in results:
        equity_df = results['equity_curve']
        equity_df.to_csv('data/backtest_equity_curve.csv', index=False)
        logger.info("\n✓ Equity curve сохранена: data/backtest_equity_curve.csv")

logger.info("\n" + "="*60)
logger.info("✓ БЭКТЕСТ ЗАВЕРШЕН")
logger.info("="*60)
