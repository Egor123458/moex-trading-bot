# 🚀 Развертывание на Яндекс Облаке

## 📋 Параметры ВМ

- **Имя:** moex-trading-bot
- **IP:** 158.160.45.252
- **Пользователь:** ubuntu
- **SSH ключ:** yandex-trading-bot
- **ОС:** Ubuntu 22.04 LTS
- **Ресурсы:** 2 vCPU, 2 ГБ RAM, 50 ГБ SSD

## 🔌 Подключение

```bash
ssh -i ~/.ssh/yandex-trading-bot ubuntu@158.160.45.252
```

## 📦 Развертывание

### Быстрый старт

```bash
# 1. Обновление системы
sudo apt-get update && sudo apt-get upgrade -y

# 2. Установка пакетов
sudo apt-get install -y python3.10 python3.10-venv python3-pip git postgresql-client curl wget build-essential libpq-dev

# 3. Клонирование
cd ~
git clone https://github.com/Egor123458/moex-trading-bot.git moex_trading_bot
cd moex_trading_bot

# 4. Развертывание
chmod +x deploy/deploy_user.sh
./deploy/deploy_user.sh

# 5. Настройка .env
nano .env
# Вставьте ваш .env файл

# 6. Запуск
chmod +x deploy/run_bot.sh deploy/stop_bot.sh deploy/status_bot.sh
./deploy/run_bot.sh
```

## 🔧 Настройка подключения к БД

### Вариант 1: БД на VK Cloud

Если БД на другой ВМ (VK Cloud), настройте подключение:

```env
# В .env используйте внешний IP БД или настройте VPN
DATABASE_URL=postgresql://admin:Admin123456@ВНЕШНИЙ_IP_БД:5432/trading_bot
```

**Важно:** Убедитесь, что:
- Firewall БД разрешает подключения с IP Яндекс Облака (158.160.45.252)
- Порт 5432 открыт

### Вариант 2: Локальная SQLite (для начала)

```env
DATABASE_URL=sqlite:///data/trading_bot.db
```

## 📊 Мониторинг

```bash
# Статус бота
cd ~/moex_trading_bot
./deploy/status_bot.sh

# Логи
tail -f logs/bot.log

# Использование ресурсов
htop
```

## 🔄 Обновление

```bash
cd ~/moex_trading_bot
./deploy/stop_bot.sh
git pull origin main
source venv/bin/activate
pip install -r requirements.txt --upgrade
./deploy/run_bot.sh
```

## ⚙️ Автозапуск

```bash
crontab -e
```

Добавьте:
```
@reboot sleep 60 && cd ~/moex_trading_bot && ./deploy/run_bot.sh >> ~/moex_trading_bot/logs/cron.log 2>&1
```

## 🔐 Безопасность

1. Настройте firewall в Яндекс Облаке
2. Используйте только необходимые порты
3. Регулярно обновляйте систему: `sudo apt-get update && sudo apt-get upgrade -y`

