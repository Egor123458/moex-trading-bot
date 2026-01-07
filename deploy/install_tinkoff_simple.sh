#!/bin/bash
# Простая установка Tinkoff Invest API - клонирование и установка в режиме разработки

echo "🔧 Установка Tinkoff Invest API..."

cd ~/moex_trading_bot
source venv/bin/activate

# Проверяем наличие git
if ! command -v git &> /dev/null; then
    echo "Установка git..."
    apt update && apt install -y git
fi

# Клонируем репозиторий в локальную директорию
if [ ! -d "tinkoff_invest_source" ]; then
    echo "Клонирование репозитория invest-python..."
    git clone https://github.com/Tinkoff/invest-python.git tinkoff_invest_source
fi

cd tinkoff_invest_source

echo "Установка в режиме разработки..."
pip install -e .

cd ..

# Проверка установки
echo "Проверка установки..."
python -c "from tinkoff.invest import Client; print('✅ Tinkoff Invest API установлен и работает!')" 2>&1

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Установка завершена успешно!"
    exit 0
else
    echo ""
    echo "❌ Ошибка установки."
    exit 1
fi

