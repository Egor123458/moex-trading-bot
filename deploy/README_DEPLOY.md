# 🚀 Инструкция по развертыванию на ВМ

## Подготовка

### 1. Подключение к ВМ приложения

```bash
# На вашем локальном компьютере
ssh -i /path/to/moex-trading-vm-0x5ulVyq.pem ubuntu@89.208.197.34

# Получение root прав
sudo bash
```

### 2. Установка необходимых инструментов

```bash
# Обновление системы
apt-get update && apt-get upgrade -y

# Установка git (если еще не установлен)
apt-get install -y git
```

## Развертывание

### Вариант 1: Автоматическое развертывание (рекомендуется)

```bash
# Клонирование репозитория
cd /tmp
git clone https://github.com/Egor123458/moex-trading-bot.git
cd moex-trading-bot

# Запуск скрипта развертывания
chmod +x deploy/deploy.sh
sudo ./deploy/deploy.sh
```

### Вариант 2: Ручное развертывание

```bash
# 1. Создание пользователя
useradd -r -s /bin/bash -d /opt/moex_trading_bot -m tradingbot

# 2. Клонирование репозитория
cd /opt
git clone https://github.com/Egor123458/moex-trading-bot.git
chown -R tradingbot:tradingbot moex_trading_bot

# 3. Создание виртуального окружения
cd moex_trading_bot
sudo -u tradingbot python3.11 -m venv venv
sudo -u tradingbot ./venv/bin/pip install -r requirements.txt

# 4. Установка systemd service
cp deploy/moex-trading-bot.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable moex-trading-bot.service
```

## Настройка

### 1. Настройка переменных окружения

```bash
# Копирование шаблона
cp .env.example .env

# Редактирование .env
nano .env
```

**Обязательные параметры в .env:**

```env
# API ключи
TINKOFF_TOKEN=your_token_here
TINKOFF_ACCOUNT_ID=your_account_id
MOEX_API_KEY=your_moex_key

# База данных
DATABASE_URL=postgresql://trading_user:password@10.0.0.129:5432/trading_bot

# Торговые параметры
INITIAL_CAPITAL=1000000
MODE=paper_trading  # или live_trading

# Telegram уведомления
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Логирование
LOG_LEVEL=INFO
```

### 2. Настройка подключения к БД

```bash
# Установка PostgreSQL клиента
apt-get install -y postgresql-client

# Запуск скрипта настройки БД
chmod +x deploy/setup_db.sh
./deploy/setup_db.sh
```

**Или вручную:**

```bash
# Создание базы данных
psql -h 10.0.0.129 -U trading_user -d postgres
CREATE DATABASE trading_bot;
\q

# Инициализация схемы БД
cd /opt/moex_trading_bot
sudo -u tradingbot ./venv/bin/python scripts/setup_database.py
```

## Запуск и управление

### Запуск сервиса

```bash
# Запуск
systemctl start moex-trading-bot

# Проверка статуса
systemctl status moex-trading-bot

# Автозапуск при загрузке системы
systemctl enable moex-trading-bot
```

### Просмотр логов

```bash
# Логи systemd
journalctl -u moex-trading-bot -f

# Логи приложения
tail -f /opt/moex_trading_bot/logs/trading/*.log
tail -f /opt/moex_trading_bot/logs/errors/*.log
```

### Управление сервисом

```bash
# Остановка
systemctl stop moex-trading-bot

# Перезапуск
systemctl restart moex-trading-bot

# Перезагрузка конфигурации
systemctl daemon-reload
systemctl restart moex-trading-bot
```

## Обновление

```bash
# Переход в директорию приложения
cd /opt/moex_trading_bot

# Остановка сервиса
systemctl stop moex-trading-bot

# Обновление кода
sudo -u tradingbot git pull origin main

# Обновление зависимостей
sudo -u tradingbot ./venv/bin/pip install -r requirements.txt --upgrade

# Запуск сервиса
systemctl start moex-trading-bot
```

## Мониторинг

### Проверка работы бота

```bash
# Статус сервиса
systemctl status moex-trading-bot

# Использование ресурсов
top -p $(pgrep -f "python.*main.py")

# Проверка подключения к БД
psql -h 10.0.0.129 -U trading_user -d trading_bot -c "SELECT COUNT(*) FROM candles;"
```

### Настройка мониторинга (опционально)

```bash
# Установка htop для мониторинга
apt-get install -y htop

# Установка netdata для детального мониторинга
bash <(curl -Ss https://my-netdata.io/kickstart.sh)
```

## Резервное копирование

### Автоматическое резервное копирование БД

Создайте скрипт `/opt/backup_db.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p "$BACKUP_DIR"

pg_dump -h 10.0.0.129 -U trading_user trading_bot > "$BACKUP_DIR/trading_bot_$DATE.sql"

# Удаление старых бэкапов (старше 7 дней)
find "$BACKUP_DIR" -name "trading_bot_*.sql" -mtime +7 -delete
```

Добавьте в crontab:

```bash
# Ежедневное резервное копирование в 3:00
0 3 * * * /opt/backup_db.sh
```

## Устранение неполадок

### Бот не запускается

```bash
# Проверка логов
journalctl -u moex-trading-bot -n 50

# Проверка прав доступа
ls -la /opt/moex_trading_bot

# Проверка виртуального окружения
/opt/moex_trading_bot/venv/bin/python --version
```

### Проблемы с подключением к БД

```bash
# Проверка доступности БД
ping 10.0.0.129
telnet 10.0.0.129 5432

# Проверка параметров подключения
cat /opt/moex_trading_bot/.env | grep DATABASE_URL
```

### Высокое использование ресурсов

```bash
# Проверка процессов
ps aux | grep python

# Ограничение ресурсов в systemd service
# Отредактируйте /etc/systemd/system/moex-trading-bot.service
# и добавьте MemoryMax=4G
```

## Безопасность

### Настройка firewall

```bash
# Разрешить только необходимые порты
ufw allow 22/tcp  # SSH
ufw enable
```

### Обновление системы

```bash
# Регулярное обновление
apt-get update && apt-get upgrade -y
```

## Контакты и поддержка

При возникновении проблем проверьте:
1. Логи: `journalctl -u moex-trading-bot`
2. Статус сервиса: `systemctl status moex-trading-bot`
3. Подключение к БД: `psql -h 10.0.0.129 -U trading_user -d trading_bot`

