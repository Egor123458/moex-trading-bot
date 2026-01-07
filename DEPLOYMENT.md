# 🚀 Быстрое развертывание на ВМ

## Подключение к ВМ

```bash
ssh -i /path/to/moex-trading-vm-0x5ulVyq.pem ubuntu@89.208.197.34
sudo bash
```

## Автоматическое развертывание

```bash
# Клонирование и запуск
cd /tmp
git clone https://github.com/Egor123458/moex-trading-bot.git
cd moex-trading-bot
chmod +x deploy/quick_start.sh
./deploy/quick_start.sh
```

Или вручную:

```bash
chmod +x deploy/deploy.sh
sudo ./deploy/deploy.sh
```

## Настройка

### 1. Настройка .env файла

```bash
nano /opt/moex_trading_bot/.env
```

Укажите:
- `TINKOFF_TOKEN` - токен Tinkoff Invest API
- `TINKOFF_ACCOUNT_ID` - ID счета
- `DATABASE_URL` - подключение к БД (например: `postgresql://user:pass@10.0.0.129:5432/trading_bot`)
- `TELEGRAM_BOT_TOKEN` и `TELEGRAM_CHAT_ID` - для уведомлений

### 2. Настройка БД

```bash
chmod +x /opt/moex_trading_bot/deploy/setup_db.sh
/opt/moex_trading_bot/deploy/setup_db.sh
```

## Запуск

```bash
# Запуск сервиса
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

## Подключение к БД

БД находится на внутренней сети:
- **IP первого члена:** 10.0.0.129
- **Порт:** 5432
- **Пользователь:** admin (или создайте trading_user)

Подключение из ВМ приложения:
```bash
psql -h 10.0.0.129 -U admin -d postgres
```

## Мониторинг

```bash
# Статус
systemctl status moex-trading-bot

# Логи
journalctl -u moex-trading-bot -n 100

# Использование ресурсов
htop
```

## Подробная документация

См. [deploy/README_DEPLOY.md](deploy/README_DEPLOY.md) для детальной инструкции.

