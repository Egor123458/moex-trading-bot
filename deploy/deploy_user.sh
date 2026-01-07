#!/bin/bash
# Скрипт развертывания торгового бота БЕЗ прав root (для обычного пользователя)

set -e

echo "🚀 Начало развертывания MOEX Trading Bot (без root прав)..."

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Переменные
APP_DIR="$HOME/moex_trading_bot"
PYTHON_VERSION="3.11"

echo -e "${GREEN}✓ Развертывание для пользователя: $(whoami)${NC}"

# Проверка Python
echo -e "${YELLOW}🐍 Проверка Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 не установлен. Установите его вручную:${NC}"
    echo "sudo apt-get install python3 python3-pip python3-venv"
    exit 1
fi

PYTHON_VER=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo -e "${GREEN}✓ Python версия: $PYTHON_VER${NC}"

# Создание директории приложения
echo -e "${YELLOW}📁 Создание директории приложения...${NC}"
mkdir -p "$APP_DIR"
cd "$APP_DIR"

# Клонирование/обновление репозитория
echo -e "${YELLOW}📥 Получение кода из GitHub...${NC}"
if [ -d "$APP_DIR/.git" ]; then
    echo "Обновление существующего репозитория..."
    git pull origin main
else
    echo "Клонирование репозитория..."
    git clone https://github.com/Egor123458/moex-trading-bot.git "$APP_DIR"
fi

# Создание виртуального окружения
echo -e "${YELLOW}🐍 Создание виртуального окружения...${NC}"
if [ ! -d "$APP_DIR/venv" ]; then
    python3 -m venv venv
fi

# Активация и обновление pip
echo -e "${YELLOW}📦 Обновление pip...${NC}"
source venv/bin/activate
pip install --upgrade pip

# Установка зависимостей
echo -e "${YELLOW}📦 Установка зависимостей...${NC}"
pip install -r requirements.txt

# Создание необходимых директорий
echo -e "${YELLOW}📁 Создание директорий...${NC}"
mkdir -p data/raw data/processed data/models data/backtest
mkdir -p logs/trading logs/errors logs/performance

# Копирование .env.example в .env если .env не существует
if [ ! -f "$APP_DIR/.env" ]; then
    echo -e "${YELLOW}⚙️  Создание .env файла из шаблона...${NC}"
    if [ -f "$APP_DIR/.env.example" ]; then
        cp "$APP_DIR/.env.example" "$APP_DIR/.env"
        echo -e "${YELLOW}⚠️  ВАЖНО: Отредактируйте $APP_DIR/.env и укажите все необходимые параметры!${NC}"
    else
        echo -e "${YELLOW}⚠️  Создайте .env файл вручную с необходимыми параметрами${NC}"
    fi
fi

echo -e "${GREEN}✅ Развертывание завершено!${NC}"
echo ""
echo -e "${YELLOW}Следующие шаги:${NC}"
echo "1. Отредактируйте $APP_DIR/.env и укажите все параметры"
echo "2. Настройте подключение к БД"
echo ""
echo -e "${YELLOW}Запуск бота:${NC}"
echo "cd $APP_DIR"
echo "source venv/bin/activate"
echo "python main.py"
echo ""
echo -e "${YELLOW}Или запустите в фоновом режиме:${NC}"
echo "nohup python main.py > logs/bot.log 2>&1 &"
echo ""

