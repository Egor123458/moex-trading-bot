#!/bin/bash
# Быстрый старт для развертывания на ВМ

echo "🚀 Быстрый старт развертывания MOEX Trading Bot"
echo ""

# Проверка подключения
read -p "Вы подключены к ВМ moex-trading-vm (89.208.197.34)? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Подключитесь к ВМ: ssh -i <ключ> ubuntu@89.208.197.34"
    exit 1
fi

# Проверка прав root
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  Запуск с правами root..."
    sudo bash "$0"
    exit $?
fi

echo "📥 Клонирование репозитория..."
cd /tmp
if [ -d "moex-trading-bot" ]; then
    rm -rf moex-trading-bot
fi
git clone https://github.com/Egor123458/moex-trading-bot.git
cd moex-trading-bot

echo "🔧 Запуск развертывания..."
chmod +x deploy/deploy.sh
./deploy/deploy.sh

echo ""
echo "✅ Развертывание завершено!"
echo ""
echo "📝 Следующие шаги:"
echo "1. Отредактируйте /opt/moex_trading_bot/.env"
echo "2. Настройте подключение к БД: ./deploy/setup_db.sh"
echo "3. Запустите: systemctl start moex-trading-bot"
echo "4. Проверьте: systemctl status moex-trading-bot"

