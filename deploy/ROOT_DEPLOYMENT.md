# 🚀 Развертывание с правами root (полная версия)

## ✅ Вы зашли как root на ВМ приложения

Отлично! Теперь можно использовать полную версию с systemd для автозапуска.

## 📋 Пошаговая инструкция

### Шаг 1: Обновление системы

```bash
apt-get update
apt-get upgrade -y
```

### Шаг 2: Установка необходимых пакетов

```bash
apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    git \
    postgresql-client \
    curl \
    wget
```

### Шаг 3: Клонирование репозитория

```bash
cd /tmp
git clone https://github.com/Egor123458/moex-trading-bot.git
cd moex-trading-bot
```

### Шаг 4: Запуск автоматического развертывания

```bash
chmod +x deploy/deploy.sh
./deploy/deploy.sh
```

Скрипт автоматически:
- ✅ Создаст пользователя `tradingbot`
- ✅ Настроит виртуальное окружение
- ✅ Установит systemd service
- ✅ Настроит автозапуск

### Шаг 5: Настройка .env файла

```bash
nano /opt/moex_trading_bot/.env
```

**Обязательно укажите:**

```env
# API ключи Tinkoff
TINKOFF_TOKEN=ваш_токен_здесь
TINKOFF_ACCOUNT_ID=ваш_account_id

# База данных (используйте ВНУТРЕННИЙ IP Master БД)
DATABASE_URL=postgresql://admin:Admin123456@10.0.0.129:5432/trading_bot

# Режим работы
MODE=paper_trading

# Telegram уведомления (опционально)
TELEGRAM_BOT_TOKEN=ваш_bot_token
TELEGRAM_CHAT_ID=ваш_chat_id

# Логирование
LOG_LEVEL=INFO
```

**Сохраните:** `Ctrl+O`, `Enter`, `Ctrl+X`

### Шаг 6: Настройка базы данных

```bash
# Проверка подключения к БД
psql -h 10.0.0.129 -U admin -d postgres
# Пароль: Admin123456

# Создание базы данных
CREATE DATABASE trading_bot;
\q
```

Или создайте отдельного пользователя:
```sql
CREATE USER trading_user WITH PASSWORD 'your_secure_password';
CREATE DATABASE trading_bot OWNER trading_user;
GRANT ALL PRIVILEGES ON DATABASE trading_bot TO trading_user;
```

### Шаг 7: Инициализация схемы БД (если есть скрипт)

```bash
cd /opt/moex_trading_bot
sudo -u tradingbot ./venv/bin/python scripts/setup_database.py
```

### Шаг 8: Запуск бота

```bash
# Запуск сервиса
systemctl start moex-trading-bot

# Включение автозапуска при загрузке системы
systemctl enable moex-trading-bot

# Проверка статуса
systemctl status moex-trading-bot
```

### Шаг 9: Проверка работы

```bash
# Просмотр логов в реальном времени
journalctl -u moex-trading-bot -f

# Или последние 100 строк
journalctl -u moex-trading-bot -n 100
```

## 🔧 Управление ботом

```bash
# Остановка
systemctl stop moex-trading-bot

# Перезапуск
systemctl restart moex-trading-bot

# Статус
systemctl status moex-trading-bot

# Отключение автозапуска
systemctl disable moex-trading-bot
```

## 🔄 Обновление бота

```bash
cd /opt/moex_trading_bot
./deploy/update.sh
```

Или вручную:
```bash
systemctl stop moex-trading-bot
cd /opt/moex_trading_bot
sudo -u tradingbot git pull origin main
sudo -u tradingbot ./venv/bin/pip install -r requirements.txt --upgrade
systemctl start moex-trading-bot
```

## 📊 Мониторинг

```bash
# Логи systemd
journalctl -u moex-trading-bot -f

# Логи приложения
tail -f /opt/moex_trading_bot/logs/trading/*.log
tail -f /opt/moex_trading_bot/logs/errors/*.log

# Использование ресурсов
top -p $(pgrep -f "python.*main.py")
```

## 🔍 Устранение проблем

### Бот не запускается

```bash
# Проверка логов
journalctl -u moex-trading-bot -n 50

# Проверка прав
ls -la /opt/moex_trading_bot

# Проверка .env
cat /opt/moex_trading_bot/.env
```

### Проблемы с подключением к БД

```bash
# Проверка доступности БД
ping 10.0.0.129
telnet 10.0.0.129 5432

# Тестовое подключение
psql -h 10.0.0.129 -U admin -d trading_bot -c "SELECT version();"
```

## ✅ Готово!

Бот должен работать 24/7 с автоматическим перезапуском при сбоях!

