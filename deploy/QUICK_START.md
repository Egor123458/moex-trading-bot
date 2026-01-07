# 🚀 Быстрый старт развертывания

## Подключение к ВМ

```powershell
ssh -i "C:\Users\Egor Galkin\Downloads\moex-trading-vm-0x5ulVyq.pem" admin@89.208.196.98
```

## Автоматическое развертывание

После подключения к ВМ выполните:

```bash
# Получение root прав
sudo bash

# Клонирование репозитория
cd /tmp
git clone https://github.com/Egor123458/moex-trading-bot.git
cd moex-trading-bot

# Запуск развертывания
chmod +x deploy/deploy.sh
./deploy/deploy.sh
```

## Настройка после развертывания

### 1. Настройка .env файла

```bash
nano /opt/moex_trading_bot/.env
```

Укажите обязательные параметры:
- `TINKOFF_TOKEN` - токен Tinkoff Invest API
- `TINKOFF_ACCOUNT_ID` - ID счета
- `DATABASE_URL` - подключение к БД (например: `postgresql://user:pass@10.0.0.129:5432/trading_bot`)
- `TELEGRAM_BOT_TOKEN` и `TELEGRAM_CHAT_ID` - для уведомлений

### 2. Запуск сервиса

```bash
# Запуск
systemctl start moex-trading-bot

# Автозапуск при загрузке
systemctl enable moex-trading-bot

# Проверка статуса
systemctl status moex-trading-bot

# Просмотр логов
journalctl -u moex-trading-bot -f
```

## Управление

```bash
# Остановка
systemctl stop moex-trading-bot

# Перезапуск
systemctl restart moex-trading-bot

# Обновление
cd /opt/moex_trading_bot
sudo ./deploy/update.sh
```

