# Шаблон .env для Finam с режимом обучения

Пример конфигурации для работы с Finam в режиме dual mode, где sandbox модель только учится (без торговли), а live модель торгует.

## Конфигурация .env

```bash
# Тип брокера
BROKER_TYPE=finam

# Режим работы (dual_mode = обе модели одновременно)
MODE=dual_mode

# Finam токен (один для обеих моделей)
FINAM_TOKEN=TXBO:01KEHQJ874S7M8XKNMY95KPFD7

# Счет Finam (один для обеих моделей)
FINAM_ACCOUNT_ID=КлФ-2012789
FINAM_SANDBOX_ACCOUNT_ID=КлФ-2012789
FINAM_LIVE_ACCOUNT_ID=КлФ-2012789

# Режим sandbox: только обучение (без торговли)
# true = sandbox только собирает данные и учится, не торгует
# false = sandbox торгует (как и live)
SANDBOX_LEARNING_ONLY=true

# Общие настройки
INITIAL_CAPITAL=1000000
DATABASE_URL=sqlite:///data/trading_bot.db

# Логирование
LOG_LEVEL=INFO

# Telegram (опционально)
# TELEGRAM_BOT_TOKEN=ваш_telegram_bot_token
# TELEGRAM_CHAT_ID=ваш_chat_id
```

## Как это работает

1. **Sandbox модель (обучение):**
   - Собирает данные с MOEX API
   - Сохраняет данные в БД
   - Генерирует сигналы для анализа
   - НЕ размещает ордера (торговля отключена)

2. **Live модель (торговля):**
   - Получает портфель
   - Генерирует сигналы
   - Размещает ордера через Finam API
   - Выполняет реальную торговлю

## Важные замечания

⚠️ **Безопасность:**
- Никогда не публикуйте токены в открытом доступе
- Не коммитьте .env файл в Git (он уже в .gitignore)
- Храните токены в безопасном месте

⚠️ **Finam не имеет отдельного sandbox режима:**
- Sandbox модель использует тот же токен и счет, но не торгует
- Только live модель выполняет реальные сделки
- Это позволяет безопасно тестировать стратегии без риска

## Проверка конфигурации

После настройки .env файла:

```bash
cd ~/moex_trading_bot
./deploy/stop_bot.sh
./deploy/run_bot.sh
tail -f logs/bot.log
```

В логах должно быть:
```
✅ Sandbox Finam клиент инициализирован
✅ Live Finam клиент инициализирован
--- Sandbox цикл обучения (без торговли) ---
--- Live торговый цикл ---
```

## Режимы работы

- `MODE=paper_trading` - только sandbox/обучение
- `MODE=live_trading` - только реальная торговля
- `MODE=dual_mode` - обе модели одновременно (рекомендуется)

## Отключение режима обучения

Если хотите, чтобы sandbox тоже торговал:

```bash
SANDBOX_LEARNING_ONLY=false
```

