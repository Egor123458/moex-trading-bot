#!/bin/bash
# Скрипт развертывания торгового бота на ВМ

set -e

echo "🚀 Начало развертывания MOEX Trading Bot..."

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Переменные
APP_DIR="/opt/moex_trading_bot"
SERVICE_USER="tradingbot"
PYTHON_VERSION="3.11"

# Проверка прав root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Пожалуйста, запустите скрипт с правами root (sudo)${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Проверка прав root пройдена${NC}"

# Обновление системы
echo -e "${YELLOW}📦 Обновление системы...${NC}"
apt-get update
apt-get upgrade -y

# Установка необходимых пакетов
echo -e "${YELLOW}📦 Установка зависимостей...${NC}"
apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    git \
    postgresql-client \
    curl \
    wget \
    supervisor \
    systemd \
    build-essential \
    libpq-dev

# Создание пользователя для приложения
if ! id "$SERVICE_USER" &>/dev/null; then
    echo -e "${YELLOW}👤 Создание пользователя $SERVICE_USER...${NC}"
    useradd -r -s /bin/bash -d "$APP_DIR" -m "$SERVICE_USER"
    echo -e "${GREEN}✓ Пользователь создан${NC}"
else
    echo -e "${GREEN}✓ Пользователь $SERVICE_USER уже существует${NC}"
fi

# Создание директории приложения
mkdir -p "$APP_DIR"
chown -R "$SERVICE_USER:$SERVICE_USER" "$APP_DIR"

# Клонирование/обновление репозитория
echo -e "${YELLOW}📥 Получение кода из GitHub...${NC}"
if [ -d "$APP_DIR/.git" ]; then
    cd "$APP_DIR"
    sudo -u "$SERVICE_USER" git pull origin main
else
    cd /tmp
    sudo -u "$SERVICE_USER" git clone https://github.com/Egor123458/moex-trading-bot.git "$APP_DIR"
fi

# Создание виртуального окружения
echo -e "${YELLOW}🐍 Создание виртуального окружения...${NC}"
cd "$APP_DIR"
sudo -u "$SERVICE_USER" python3.11 -m venv venv
sudo -u "$SERVICE_USER" ./venv/bin/pip install --upgrade pip
sudo -u "$SERVICE_USER" ./venv/bin/pip install -r requirements.txt

# Создание необходимых директорий
echo -e "${YELLOW}📁 Создание директорий...${NC}"
sudo -u "$SERVICE_USER" mkdir -p "$APP_DIR/data/raw" "$APP_DIR/data/processed" "$APP_DIR/data/models" "$APP_DIR/data/backtest"
sudo -u "$SERVICE_USER" mkdir -p "$APP_DIR/logs/trading" "$APP_DIR/logs/errors" "$APP_DIR/logs/performance"

# Копирование .env.example в .env если .env не существует
if [ ! -f "$APP_DIR/.env" ]; then
    echo -e "${YELLOW}⚙️  Создание .env файла из шаблона...${NC}"
    if [ -f "$APP_DIR/.env.example" ]; then
        sudo -u "$SERVICE_USER" cp "$APP_DIR/.env.example" "$APP_DIR/.env"
        echo -e "${YELLOW}⚠️  ВАЖНО: Отредактируйте $APP_DIR/.env и укажите все необходимые параметры!${NC}"
    fi
fi

# Установка systemd service
echo -e "${YELLOW}⚙️  Установка systemd service...${NC}"
cp "$APP_DIR/deploy/moex-trading-bot.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable moex-trading-bot.service

echo -e "${GREEN}✓ Systemd service установлен${NC}"

# Установка прав на файлы
chown -R "$SERVICE_USER:$SERVICE_USER" "$APP_DIR"

echo -e "${GREEN}✅ Развертывание завершено!${NC}"
echo ""
echo -e "${YELLOW}Следующие шаги:${NC}"
echo "1. Отредактируйте $APP_DIR/.env и укажите все параметры"
echo "2. Проверьте настройки подключения к БД"
echo "3. Запустите сервис: sudo systemctl start moex-trading-bot"
echo "4. Проверьте статус: sudo systemctl status moex-trading-bot"
echo "5. Просмотр логов: sudo journalctl -u moex-trading-bot -f"

