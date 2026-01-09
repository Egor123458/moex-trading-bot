# Быстрое исправление проблем

## Проблема 1: Permission denied для скриптов

Выполните на ВМ:

```bash
cd ~/moex_trading_bot
chmod +x deploy/run_bot.sh
chmod +x deploy/stop_bot.sh
chmod +x deploy/*.sh

# Проверка прав
ls -la deploy/*.sh
```

Теперь скрипты должны работать:
```bash
./deploy/run_bot.sh
./deploy/stop_bot.sh
```

## Проблема 2: Баланс показывает 0

### Вариант A: Проверка токена и счета

```bash
# Проверьте .env файл
cat .env | grep FINAM

# Должно быть:
# FINAM_TOKEN=TXBO:01KEHQJ874S7M8XKNMY95KPFD7
# FINAM_ACCOUNT_ID=КлФ-2012789
```

### Вариант B: Тестирование Finam API вручную

```bash
cd ~/moex_trading_bot
source venv/bin/activate

python3 << EOF
import requests
import os
from dotenv import load_dotenv

load_dotenv()

token = os.getenv('FINAM_TOKEN')
account_id = os.getenv('FINAM_ACCOUNT_ID')

print(f"Токен: {token[:20]}...")
print(f"Счет: {account_id}")

# Тест API
url = "https://trade-api.finam.ru/api/v1/portfolio"
headers = {
    "X-Api-Key": token,
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
params = {"accountId": account_id} if account_id else {}

response = requests.get(url, headers=headers, params=params, timeout=10)
print(f"\nСтатус: {response.status_code}")
print(f"Ответ: {response.text[:500]}")
EOF
```

### Вариант C: Обновление кода

После обновления кода (который я только что сделал), перезапустите бота:

```bash
cd ~/moex_trading_bot
git pull origin main
./deploy/stop_bot.sh
source venv/bin/activate
pip install -r requirements.txt
./deploy/run_bot.sh
tail -f logs/bot.log
```

## Проблема 3: Telegram бот не поднялся

### Проверка настроек Telegram

```bash
# Проверьте .env файл
cat .env | grep TELEGRAM

# Должно быть:
# TELEGRAM_BOT_TOKEN=ваш_токен
# TELEGRAM_CHAT_ID=ваш_chat_id
```

### Запуск Telegram бота отдельно (для теста)

```bash
cd ~/moex_trading_bot
source venv/bin/activate

python3 << EOF
from config.settings import settings
print(f"Telegram токен: {settings.TELEGRAM_BOT_TOKEN[:20] if settings.TELEGRAM_BOT_TOKEN else 'НЕ УКАЗАН'}...")
print(f"Telegram chat_id: {settings.TELEGRAM_CHAT_ID if settings.TELEGRAM_CHAT_ID else 'НЕ УКАЗАН'}")
EOF
```

### Если токены не указаны

Добавьте в .env:
```bash
nano .env
```

Добавьте строки:
```bash
TELEGRAM_BOT_TOKEN=ваш_токен_бота
TELEGRAM_CHAT_ID=ваш_chat_id
```

Сохраните: `Ctrl+O`, `Enter`, `Ctrl+X`

### Запуск Telegram бота вручную (для теста)

```bash
cd ~/moex_trading_bot
source venv/bin/activate
python src/monitoring/telegram_bot_service.py
```

## Полное решение всех проблем

Выполните все команды по порядку:

```bash
# 1. Исправление прав на скрипты
cd ~/moex_trading_bot
chmod +x deploy/*.sh

# 2. Обновление кода
git pull origin main

# 3. Обновление зависимостей
source venv/bin/activate
pip install -r requirements.txt

# 4. Проверка .env
cat .env

# 5. Перезапуск бота
./deploy/stop_bot.sh
./deploy/run_bot.sh

# 6. Проверка логов
tail -f logs/bot.log
```

## Что должно быть в логах

После исправлений в логах должно быть:

```
✅ Sandbox Finam клиент инициализирован
✅ Live Finam клиент инициализирован
Портфель Finam: позиций=X, total_value=XXXXX, cash=XXXXX
✅ Подключение к БД установлено
✅ MOEX API инициализирован
```

Если баланс все еще 0, проверьте:
1. Правильность токена Finam
2. Правильность номера счета
3. Доступность Finam API (может быть блокировка по IP)

