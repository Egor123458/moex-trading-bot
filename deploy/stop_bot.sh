#!/bin/bash
# Скрипт остановки бота

APP_DIR="$HOME/moex_trading_bot"
PID_FILE="$APP_DIR/bot.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "❌ Файл PID не найден. Бот, вероятно, не запущен."
    exit 1
fi

PID=$(cat "$PID_FILE")

if ps -p "$PID" > /dev/null 2>&1; then
    echo "🛑 Остановка бота (PID: $PID)..."
    kill "$PID"
    
    # Ждем завершения
    sleep 2
    
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "⚠️  Принудительная остановка..."
        kill -9 "$PID"
    fi
    
    rm -f "$PID_FILE"
    echo "✅ Бот остановлен"
else
    echo "⚠️  Процесс с PID $PID не найден"
    rm -f "$PID_FILE"
fi

