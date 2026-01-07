#!/bin/bash
# Скрипт проверки статуса бота

APP_DIR="$HOME/moex_trading_bot"
PID_FILE="$APP_DIR/bot.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "❌ Бот не запущен (файл PID не найден)"
    exit 1
fi

PID=$(cat "$PID_FILE")

if ps -p "$PID" > /dev/null 2>&1; then
    echo "✅ Бот запущен (PID: $PID)"
    echo ""
    echo "📊 Использование ресурсов:"
    ps -p "$PID" -o pid,pcpu,pmem,etime,cmd
    echo ""
    echo "📋 Последние строки лога:"
    tail -n 10 "$APP_DIR/logs/bot.log" 2>/dev/null || echo "Лог файл не найден"
else
    echo "❌ Бот не запущен (процесс не найден)"
    rm -f "$PID_FILE"
fi

