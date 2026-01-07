#!/bin/bash
# Ручная установка Tinkoff Invest API с GitHub

echo "🔧 Установка Tinkoff Invest API с GitHub..."

# Активируем виртуальное окружение
source venv/bin/activate

# Проверяем наличие git
if ! command -v git &> /dev/null; then
    echo "Установка git..."
    apt update && apt install -y git
fi

# Устанавливаем зависимости
echo "Установка зависимостей..."
pip install grpcio protobuf cachetools deprecation python-dateutil

# Устанавливаем напрямую с GitHub
echo "Установка invest-python с GitHub..."
pip install git+https://github.com/Tinkoff/invest-python.git

# Проверка установки
echo "Проверка установки..."
python -c "from tinkoff.invest import Client; print('✅ Tinkoff Invest API установлен и работает!')" 2>&1

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Установка завершена успешно!"
    exit 0
else
    echo ""
    echo "❌ Ошибка установки. Проверьте логи выше."
    exit 1
fi

