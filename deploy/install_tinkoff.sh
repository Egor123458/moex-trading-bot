#!/bin/bash
# Скрипт для установки Tinkoff Invest API библиотеки

echo "🔧 Установка Tinkoff Invest API библиотеки..."

# Активируем виртуальное окружение
source venv/bin/activate

# Пробуем установить tinkoff-investments (официальная библиотека)
echo "Попытка установки tinkoff-investments..."
pip install tinkoff-investments 2>&1 | tee /tmp/tinkoff_install.log
INSTALL_RESULT=$?

if [ $INSTALL_RESULT -eq 0 ]; then
    # Проверяем, что библиотека действительно установлена
    python -c "from tinkoff.invest import Client" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "✅ tinkoff-investments установлен успешно"
        exit 0
    else
        echo "⚠️  Установка завершилась, но библиотека не работает"
    fi
fi

# Если не получилось, пробуем установить напрямую с GitHub
echo "Попытка установки с GitHub..."
pip install git+https://github.com/Tinkoff/invest-python.git 2>&1 | tee -a /tmp/tinkoff_install.log
INSTALL_RESULT=$?

if [ $INSTALL_RESULT -eq 0 ]; then
    # Проверяем, что библиотека действительно установлена
    python -c "from tinkoff.invest import Client" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "✅ invest-python установлен с GitHub успешно"
        exit 0
    else
        echo "⚠️  Установка завершилась, но библиотека не работает"
    fi
fi

# Если не получилось, пробуем tinkoff-invest
echo "Попытка установки tinkoff-invest..."
pip install tinkoff-invest 2>&1 | tee -a /tmp/tinkoff_install.log
INSTALL_RESULT=$?

if [ $INSTALL_RESULT -eq 0 ]; then
    # Проверяем, что библиотека действительно установлена
    python -c "from tinkoff.invest import Client" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "✅ tinkoff-invest установлен успешно"
        exit 0
    else
        echo "⚠️  Установка завершилась, но библиотека не работает"
    fi
fi

# Если все не установились, выводим ошибку
echo "❌ Не удалось установить ни одну библиотеку Tinkoff"
echo "Проверьте логи: cat /tmp/tinkoff_install.log"
echo ""
echo "Попробуйте установить вручную:"
echo "  pip install tinkoff-investments"
echo "  ИЛИ"
echo "  pip install git+https://github.com/Tinkoff/invest-python.git"
exit 1

