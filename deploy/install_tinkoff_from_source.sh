#!/bin/bash
# Установка Tinkoff Invest API из исходников GitHub

echo "🔧 Установка Tinkoff Invest API из исходников..."

# Активируем виртуальное окружение
source venv/bin/activate

# Проверяем наличие git
if ! command -v git &> /dev/null; then
    echo "Установка git..."
    apt update && apt install -y git
fi

# Создаем временную директорию
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

echo "Клонирование репозитория..."
git clone https://github.com/Tinkoff/invest-python.git
cd invest-python

echo "Установка зависимостей..."
pip install -e .

# Возвращаемся в рабочую директорию
cd ~/moex_trading_bot

# Проверка установки
echo "Проверка установки..."
python -c "from tinkoff.invest import Client; print('✅ Tinkoff Invest API установлен и работает!')" 2>&1

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Установка завершена успешно!"
    rm -rf "$TEMP_DIR"
    exit 0
else
    echo ""
    echo "❌ Ошибка установки. Проверьте логи выше."
    echo "Временная директория: $TEMP_DIR"
    exit 1
fi

