#!/bin/bash
# Скрипт запуска бота в фоновом режиме (без systemd)

APP_DIR="$HOME/moex_trading_bot"
PID_FILE="$APP_DIR/bot.pid"
LOG_FILE="$APP_DIR/logs/bot.log"

cd "$APP_DIR"

# Проверка, не запущен ли уже бот
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "❌ Бот уже запущен (PID: $OLD_PID)"
        echo "Остановите его командой: ./deploy/stop_bot.sh"
        exit 1
    else
        rm -f "$PID_FILE"
    fi
fi

# Активация виртуального окружения и запуск
echo "🚀 Запуск бота..."
source venv/bin/activate
nohup python main.py > "$LOG_FILE" 2>&1 &
BOT_PID=$!

# Сохранение PID
echo $BOT_PID > "$PID_FILE"

echo "✅ Бот запущен (PID: $BOT_PID)"
echo "📋 Логи: tail -f $LOG_FILE"
echo "🛑 Остановка: ./deploy/stop_bot.sh"

