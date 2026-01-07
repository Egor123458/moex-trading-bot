#!/bin/bash
# Скрипт для установки Tinkoff Invest API библиотеки

echo "🔧 Установка Tinkoff Invest API библиотеки..."

# Активируем виртуальное окружение
source venv/bin/activate

# Пробуем установить invest-python (официальная библиотека)
echo "Попытка установки invest-python..."
pip install invest-python 2>&1 | tee /tmp/tinkoff_install.log

if [ $? -eq 0 ]; then
    echo "✅ invest-python установлен успешно"
    exit 0
fi

# Если не получилось, пробуем tinkoff-invest
echo "Попытка установки tinkoff-invest..."
pip install tinkoff-invest 2>&1 | tee -a /tmp/tinkoff_install.log

if [ $? -eq 0 ]; then
    echo "✅ tinkoff-invest установлен успешно"
    exit 0
fi

# Если оба не установились, выводим ошибку
echo "❌ Не удалось установить ни одну библиотеку Tinkoff"
echo "Проверьте логи: cat /tmp/tinkoff_install.log"
exit 1

