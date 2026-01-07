#!/bin/bash
# Скрипт обновления торгового бота

set -e

APP_DIR="/opt/moex_trading_bot"
SERVICE_USER="tradingbot"
SERVICE_NAME="moex-trading-bot"

echo "🔄 Обновление MOEX Trading Bot..."

# Проверка прав
if [ "$EUID" -ne 0 ]; then 
    echo "Пожалуйста, запустите скрипт с правами root (sudo)"
    exit 1
fi

# Остановка сервиса
echo "⏹️  Остановка сервиса..."
systemctl stop "$SERVICE_NAME"

# Обновление кода
echo "📥 Обновление кода из GitHub..."
cd "$APP_DIR"
sudo -u "$SERVICE_USER" git pull origin main

# Обновление зависимостей
echo "📦 Обновление зависимостей..."
sudo -u "$SERVICE_USER" "$APP_DIR/venv/bin/pip install -r requirements.txt --upgrade

# Применение миграций БД (если есть)
if [ -f "$APP_DIR/scripts/migrate_db.py" ]; then
    echo "🗄️  Применение миграций БД..."
    sudo -u "$SERVICE_USER" "$APP_DIR/venv/bin/python" "$APP_DIR/scripts/migrate_db.py"
fi

# Перезапуск сервиса
echo "▶️  Запуск сервиса..."
systemctl start "$SERVICE_NAME"

# Проверка статуса
sleep 3
if systemctl is-active --quiet "$SERVICE_NAME"; then
    echo "✅ Обновление завершено успешно!"
    systemctl status "$SERVICE_NAME" --no-pager
else
    echo "❌ Ошибка при запуске сервиса. Проверьте логи:"
    echo "journalctl -u $SERVICE_NAME -n 50"
    exit 1
fi

