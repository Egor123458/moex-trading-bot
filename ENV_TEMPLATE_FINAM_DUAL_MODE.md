# Шаблон .env для Finam Dual Mode

Пример конфигурации для работы с Finam в режиме dual mode (одновременно sandbox и live).

## Вариант 1: Один токен для обеих моделей

Если у вас один токен Finam, но два разных счета (один для тестирования, другой для реальной торговли):

```bash
# Тип брокера
BROKER_TYPE=finam

# Режим работы (dual_mode = обе модели одновременно)
MODE=dual_mode

# Finam токен (один токен для обеих моделей)
FINAM_TOKEN=TXBO:01KED7KN7VRGJ0GM8CZN9CNJ9G

# Счета Finam
FINAM_SANDBOX_ACCOUNT_ID=ваш_счет_для_тестирования
FINAM_LIVE_ACCOUNT_ID=ваш_счет_для_реальной_торговли

# Если используете один счет для обеих моделей, укажите его в обоих полях:
# FINAM_SANDBOX_ACCOUNT_ID=ваш_номер_счета
# FINAM_LIVE_ACCOUNT_ID=ваш_номер_счета

# Общие настройки
INITIAL_CAPITAL=1000000
DATABASE_URL=sqlite:///data/trading_bot.db

# Telegram (опционально)
TELEGRAM_BOT_TOKEN=ваш_telegram_bot_token
TELEGRAM_CHAT_ID=ваш_chat_id
```

## Вариант 2: Разные токены для sandbox и live

Если у вас два разных токена Finam:

```bash
# Тип брокера
BROKER_TYPE=finam

# Режим работы
MODE=dual_mode

# Finam токены (разные для sandbox и live)
FINAM_SANDBOX_TOKEN=токен_для_тестирования
FINAM_LIVE_TOKEN=токен_для_реальной_торговли

# Счета Finam
FINAM_SANDBOX_ACCOUNT_ID=счет_для_тестирования
FINAM_LIVE_ACCOUNT_ID=счет_для_реальной_торговли

# Общие настройки
INITIAL_CAPITAL=1000000
DATABASE_URL=sqlite:///data/trading_bot.db
```

## Вариант 3: Один счет, один токен (рекомендуется для начала)

Если у вас пока один токен и один счет, используйте его для обеих моделей:

```bash
# Тип брокера
BROKER_TYPE=finam

# Режим работы
MODE=dual_mode

# Finam токен (один для обеих моделей)
FINAM_TOKEN=TXBO:01KED7KN7VRGJ0GM8CZN9CNJ9G

# Один счет для обеих моделей
FINAM_ACCOUNT_ID=ваш_номер_счета
FINAM_SANDBOX_ACCOUNT_ID=ваш_номер_счета
FINAM_LIVE_ACCOUNT_ID=ваш_номер_счета

# Общие настройки
INITIAL_CAPITAL=1000000
DATABASE_URL=sqlite:///data/trading_bot.db
```

## Как узнать номер счета Finam?

1. Войдите в личный кабинет Финама
2. Перейдите в раздел "Мои счета" или "Портфель"
3. Найдите номер вашего брокерского счета
4. Обычно это формат: `L01-12345678` или просто `12345678`

## Важные замечания

⚠️ **Безопасность:**
- Никогда не публикуйте токены в открытом доступе
- Не коммитьте .env файл в Git (он уже в .gitignore)
- Храните токены в безопасном месте

⚠️ **Finam не имеет отдельного sandbox режима:**
- Для тестирования используйте отдельный счет с небольшим капиталом
- Или используйте один счет, но будьте осторожны с реальной торговлей

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
--- Sandbox торговый цикл ---
--- Live торговый цикл ---
```

## Режимы работы

- `MODE=paper_trading` - только sandbox/тестирование
- `MODE=live_trading` - только реальная торговля
- `MODE=dual_mode` - обе модели одновременно (рекомендуется)

