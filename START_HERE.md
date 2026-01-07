# 🎯 Начните отсюда - Развертывание на ВМ

## ✅ Шаг 1: Подключение к ВМ

**На вашем локальном компьютере (PowerShell):**

```powershell
ssh -i "C:\Users\Egor Galkin\Downloads\moex-trading-vm-0x5ulVyq.pem" admin@89.208.196.98
```

## ✅ Шаг 2: Развертывание бота

**После подключения к ВМ выполните:**

```bash
# 1. Получение root прав
sudo bash

# 2. Клонирование репозитория
cd /tmp
git clone https://github.com/Egor123458/moex-trading-bot.git
cd moex-trading-bot

# 3. Запуск автоматического развертывания
chmod +x deploy/deploy.sh
./deploy/deploy.sh
```

Скрипт автоматически:
- ✅ Установит все зависимости
- ✅ Создаст пользователя `tradingbot`
- ✅ Настроит виртуальное окружение Python
- ✅ Установит systemd service для автозапуска

## ✅ Шаг 3: Настройка переменных окружения

```bash
# Редактирование .env файла
nano /opt/moex_trading_bot/.env
```

**Обязательно укажите:**

```env
# API ключи Tinkoff
TINKOFF_TOKEN=ваш_токен_здесь
TINKOFF_ACCOUNT_ID=ваш_account_id

# База данных (IP первого члена кластера: 10.0.0.129)
DATABASE_URL=postgresql://trading_user:пароль@10.0.0.129:5432/trading_bot

# Режим работы
MODE=paper_trading  # или live_trading для реальной торговли

# Telegram уведомления (опционально)
TELEGRAM_BOT_TOKEN=ваш_bot_token
TELEGRAM_CHAT_ID=ваш_chat_id
```

**Сохраните:** `Ctrl+O`, `Enter`, `Ctrl+X`

## ✅ Шаг 4: Настройка базы данных (если нужно)

```bash
# Если база данных еще не создана
chmod +x /opt/moex_trading_bot/deploy/setup_db.sh
/opt/moex_trading_bot/deploy/setup_db.sh
```

Или вручную:
```bash
# Подключение к БД
psql -h 10.0.0.129 -U admin -d postgres

# Создание базы данных
CREATE DATABASE trading_bot;
\q

# Инициализация схемы
cd /opt/moex_trading_bot
sudo -u tradingbot ./venv/bin/python scripts/setup_database.py
```

## ✅ Шаг 5: Запуск бота

```bash
# Запуск сервиса
systemctl start moex-trading-bot

# Включение автозапуска при загрузке системы
systemctl enable moex-trading-bot

# Проверка статуса
systemctl status moex-trading-bot
```

## ✅ Шаг 6: Проверка работы

```bash
# Просмотр логов в реальном времени
journalctl -u moex-trading-bot -f

# Или просмотр последних 100 строк
journalctl -u moex-trading-bot -n 100
```

## 📋 Полезные команды

### Управление сервисом

```bash
# Остановка
systemctl stop moex-trading-bot

# Перезапуск
systemctl restart moex-trading-bot

# Статус
systemctl status moex-trading-bot
```

### Обновление бота

```bash
cd /opt/moex_trading_bot
sudo ./deploy/update.sh
```

### Просмотр логов

```bash
# Systemd логи
journalctl -u moex-trading-bot -f

# Логи приложения
tail -f /opt/moex_trading_bot/logs/trading/*.log
tail -f /opt/moex_trading_bot/logs/errors/*.log
```

## 🔧 Устранение проблем

### Бот не запускается

```bash
# Проверка логов
journalctl -u moex-trading-bot -n 50

# Проверка прав
ls -la /opt/moex_trading_bot

# Проверка .env файла
cat /opt/moex_trading_bot/.env
```

### Проблемы с подключением к БД

```bash
# Проверка доступности БД
ping 10.0.0.129
telnet 10.0.0.129 5432

# Проверка параметров в .env
grep DATABASE_URL /opt/moex_trading_bot/.env
```

## 📞 Поддержка

Если возникли проблемы:
1. Проверьте логи: `journalctl -u moex-trading-bot -n 100`
2. Проверьте статус: `systemctl status moex-trading-bot`
3. Убедитесь, что .env файл настроен правильно

---

**Готово! Бот должен работать 24/7 на ВМ** 🎉

