# Руководство по получению API токенов

Подробные инструкции по получению API токенов для каждого брокера.

---

## 1. Finam API

### Шаг 1: Откройте счет в Финаме
1. Перейдите на https://www.finam.ru/
2. Зарегистрируйтесь и откройте брокерский счет
3. Пополните счет (для реальной торговли)

### Шаг 2: Получите API токен
1. Войдите в личный кабинет Финама
2. Перейдите в раздел **"API"** или **"Торговые приложения"**
3. Создайте новое приложение/токен
4. Скопируйте полученный токен

### Шаг 3: Получите Account ID
1. В личном кабинете найдите номер вашего счета
2. Обычно это формат: `L01-12345678` или просто номер счета

### Шаг 4: Настройте .env
```bash
BROKER_TYPE=finam
FINAM_TOKEN=ваш_токен_из_личного_кабинета
FINAM_ACCOUNT_ID=ваш_номер_счета
```

### Документация Finam:
- Официальный сайт: https://www.finam.ru/
- API документация: https://www.finam.ru/profile/moex-aktsii/sber/export/
- Поддержка: support@finam.ru

---

## 2. Alor Open API

### Шаг 1: Откройте счет в Alor
1. Перейдите на https://alor.ru/
2. Зарегистрируйтесь и откройте брокерский счет
3. Пополните счет (для реальной торговли)

### Шаг 2: Получите JWT токен
1. Перейдите на https://alor.dev/
2. Войдите через ваш брокерский счет Alor
3. Перейдите в раздел **"Токены"** или **"API Keys"**
4. Создайте новый токен (JWT)
5. Скопируйте полученный токен

### Шаг 3: Получите Account ID
1. В личном кабинете Alor найдите номер счета
2. Формат обычно: `L01-00000F00` или `D00000`
3. Это ваш **Trade Server Code**

### Шаг 4: Настройте .env
```bash
BROKER_TYPE=alor
ALOR_TOKEN=ваш_jwt_токен_из_alor.dev
ALOR_ACCOUNT_ID=L01-00000F00  # ваш номер счета
```

### Документация Alor:
- Официальный сайт: https://alor.ru/
- API документация: https://alor.dev/
- Примеры кода: https://github.com/alor-tools
- Поддержка: support@alor.ru

---

## 3. Tinkoff Invest API

### Шаг 1: Откройте счет в Тинькофф Инвестициях
1. Перейдите на https://www.tinkoff.ru/invest/
2. Зарегистрируйтесь и откройте брокерский счет
3. Пополните счет (для реальной торговли)

### Шаг 2: Получите API токен
1. Войдите в личный кабинет Тинькофф Инвестиций
2. Перейдите в **"Настройки"** → **"API"**
3. Создайте новый токен для торговли
4. Скопируйте полученный токен

### Шаг 3: Получите Account ID
1. В личном кабинете найдите номер вашего счета
2. Обычно это формат: `12345678-1234-1234-1234-123456789012`

### Шаг 4: Настройте .env
```bash
BROKER_TYPE=tinkoff
TINKOFF_SANDBOX_TOKENS=ваш_токен_для_песочницы
TINKOFF_LIVE_TOKENS=ваш_токен_для_реальной_торговли
TINKOFF_SANDBOX_ACCOUNT_ID=ваш_account_id_песочницы
TINKOFF_LIVE_ACCOUNT_ID=ваш_account_id_реальной_торговли
```

### Документация Tinkoff:
- Официальный сайт: https://www.tinkoff.ru/invest/
- API документация: https://tinkoff.github.io/investAPI/
- GitHub: https://github.com/Tinkoff/invest-python

---

## 4. Paper Trading (Без API токена)

Paper Trading не требует API токена! Просто используйте:

```bash
BROKER_TYPE=paper
MODE=paper_trading
INITIAL_CAPITAL=1000000
```

---

## Проверка токенов

После настройки токенов проверьте их работу:

### Для Finam:
```bash
curl -H "X-Api-Key: ваш_токен" https://trade-api.finam.ru/api/v1/portfolio
```

### Для Alor:
```bash
curl -H "Authorization: Bearer ваш_токен" https://api.alor.ru/md/v2/portfolios/ваш_account_id
```

### Для Tinkoff:
```python
from tinkoff.invest import Client
with Client("ваш_токен", sandbox=True) as client:
    print(client.users.get_accounts())
```

---

## Безопасность

⚠️ **ВАЖНО:**
1. **Никогда не публикуйте токены** в открытом доступе
2. **Не коммитьте .env файл** в Git (он уже в .gitignore)
3. **Используйте разные токены** для sandbox и live торговли
4. **Регулярно обновляйте токены** (раз в 3-6 месяцев)
5. **Ограничьте права токенов** (только необходимые разрешения)

---

## Частые проблемы

### Токен не работает
- Проверьте правильность скопированного токена (без пробелов)
- Убедитесь, что токен не истек
- Проверьте права токена (должны быть разрешения на торговлю)

### Account ID не найден
- Проверьте формат Account ID (может отличаться у разных брокеров)
- Убедитесь, что используете правильный счет (не ИИС, если нужен обычный)

### Sandbox vs Live
- **Sandbox** - для тестирования, виртуальные деньги
- **Live** - реальная торговля, реальные деньги
- Используйте sandbox для разработки и тестирования!

---

## Поддержка

Если возникли проблемы:
1. Проверьте логи бота: `tail -f logs/bot.log`
2. Обратитесь в поддержку брокера
3. Проверьте документацию API брокера

---

## Пример полного .env файла

```bash
# Выбор брокера: paper, finam, alor, tinkoff
BROKER_TYPE=paper

# Finam настройки
FINAM_TOKEN=
FINAM_ACCOUNT_ID=

# Alor настройки
ALOR_TOKEN=
ALOR_ACCOUNT_ID=

# Tinkoff настройки
TINKOFF_SANDBOX_TOKENS=
TINKOFF_LIVE_TOKENS=
TINKOFF_SANDBOX_ACCOUNT_ID=
TINKOFF_LIVE_ACCOUNT_ID=

# Общие настройки
MODE=paper_trading
INITIAL_CAPITAL=1000000
DATABASE_URL=sqlite:///data/trading_bot.db
```

---

## Следующие шаги

1. Получите токены у выбранного брокера
2. Добавьте их в `.env` файл
3. Установите `BROKER_TYPE` в `.env`
4. Перезапустите бота: `./deploy/stop_bot.sh && ./deploy/run_bot.sh`
5. Проверьте логи: `tail -f logs/bot.log`

