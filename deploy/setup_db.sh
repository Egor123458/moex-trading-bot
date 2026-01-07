#!/bin/bash
# Скрипт настройки подключения к PostgreSQL кластеру

set -e

echo "🗄️  Настройка подключения к базе данных..."

# Параметры подключения (замените на ваши)
DB_HOST="10.0.0.129"  # IP первого члена кластера
DB_PORT="5432"
DB_NAME="trading_bot"
DB_USER="trading_user"
DB_PASSWORD=""  # Будет запрошен

# Запрос пароля если не указан
if [ -z "$DB_PASSWORD" ]; then
    read -sp "Введите пароль для пользователя БД: " DB_PASSWORD
    echo
fi

# Проверка подключения
echo "Проверка подключения к БД..."
export PGPASSWORD="$DB_PASSWORD"
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c "SELECT version();" || {
    echo "❌ Ошибка подключения к БД. Проверьте параметры."
    exit 1
}

# Создание базы данных если не существует
echo "Создание базы данных $DB_NAME..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres <<EOF
SELECT 'CREATE DATABASE $DB_NAME'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$DB_NAME')\gexec
EOF

echo "✅ База данных настроена!"

# Обновление .env файла
ENV_FILE="/opt/moex_trading_bot/.env"
if [ -f "$ENV_FILE" ]; then
    echo "Обновление .env файла..."
    sed -i "s|DATABASE_URL=.*|DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME|g" "$ENV_FILE"
    echo "✅ .env файл обновлен"
fi

unset PGPASSWORD

