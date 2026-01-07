# Альтернативы Tinkoff Invest API

Если у вас возникли проблемы с установкой Tinkoff Invest API, вы можете использовать альтернативные брокеры или режим Paper Trading.

## Доступные варианты

### 1. Paper Trading (Рекомендуется для начала) ✅

**Преимущества:**
- Не требует установки дополнительных библиотек
- Не требует API токенов
- Полностью безопасно для тестирования
- Использует реальные данные MOEX для цен

**Настройка:**
```bash
# В .env файле
BROKER_TYPE=paper
MODE=paper_trading
INITIAL_CAPITAL=1000000
```

**Как работает:**
- Бот использует реальные цены с MOEX API
- Торговля происходит виртуально (без реальных денег)
- Идеально для тестирования стратегий

---

### 2. Finam API

**Преимущества:**
- Популярный российский брокер
- Бесплатный доступ к историческим данным
- API для торговли (требуется открытие счета)

**Настройка:**
```bash
# В .env файле
BROKER_TYPE=finam
FINAM_TOKEN=ваш_токен_finam
FINAM_ACCOUNT_ID=ваш_account_id
```

**Регистрация:**
1. Откройте счет в Финаме: https://www.finam.ru/
2. Получите API токен в личном кабинете
3. Укажите токен в `.env`

**Документация:** https://www.finam.ru/profile/moex-aktsii/sber/export/

---

### 3. Alor Open API

**Преимущества:**
- Современный REST API
- Хорошая документация
- Поддержка sandbox режима

**Настройка:**
```bash
# В .env файле
BROKER_TYPE=alor
ALOR_TOKEN=ваш_jwt_токен_alor
ALOR_ACCOUNT_ID=ваш_account_id  # Например: L01-00000F00
```

**Регистрация:**
1. Откройте счет в Alor: https://alor.ru/
2. Получите JWT токен: https://alor.dev/
3. Укажите токен и account_id в `.env`

**Документация:** https://alor.dev/

---

### 4. Tinkoff Invest API (если удастся установить)

**Настройка:**
```bash
# В .env файле
BROKER_TYPE=tinkoff
TINKOFF_SANDBOX_TOKENS=ваш_токен
TINKOFF_SANDBOX_ACCOUNT_ID=ваш_account_id
```

**Установка библиотеки:**
```bash
cd ~/moex_trading_bot
source venv/bin/activate
git clone https://github.com/Tinkoff/invest-python.git tinkoff_invest_source
cd tinkoff_invest_source
pip install -e .
cd ..
```

---

## Быстрый старт с Paper Trading

1. **Обновите `.env` файл:**
```bash
BROKER_TYPE=paper
MODE=paper_trading
INITIAL_CAPITAL=1000000
```

2. **Запустите бота:**
```bash
cd ~/moex_trading_bot
./deploy/stop_bot.sh
./deploy/run_bot.sh
tail -f logs/bot.log
```

3. **Проверьте работу:**
Бот будет торговать виртуально, используя реальные цены с MOEX.

---

## Сравнение брокеров

| Брокер | Требует токен | Sandbox | Сложность установки | Рекомендация |
|--------|---------------|---------|---------------------|--------------|
| Paper Trading | ❌ | ✅ | ⭐ Легко | ✅ Для тестирования |
| Finam | ✅ | ❌ | ⭐⭐ Средне | ✅ Для реальной торговли |
| Alor | ✅ | ✅ | ⭐⭐ Средне | ✅ Для реальной торговли |
| Tinkoff | ✅ | ✅ | ⭐⭐⭐ Сложно | ⚠️ Проблемы с установкой |

---

## Переключение между брокерами

Вы можете легко переключаться между брокерами, изменив `BROKER_TYPE` в `.env`:

```bash
# Paper Trading
BROKER_TYPE=paper

# Finam
BROKER_TYPE=finam
FINAM_TOKEN=ваш_токен

# Alor
BROKER_TYPE=alor
ALOR_TOKEN=ваш_токен

# Tinkoff
BROKER_TYPE=tinkoff
TINKOFF_SANDBOX_TOKENS=ваш_токен
```

После изменения перезапустите бота:
```bash
./deploy/stop_bot.sh
./deploy/run_bot.sh
```

---

## Рекомендации

1. **Для начала:** Используйте Paper Trading для тестирования стратегий
2. **Для реальной торговли:** Выберите Finam или Alor (проще в установке, чем Tinkoff)
3. **Для разработки:** Paper Trading идеален - не требует токенов и работает сразу

---

## Поддержка

Если у вас возникли проблемы с настройкой брокера, проверьте:
1. Правильность токенов в `.env`
2. Логи бота: `tail -f logs/bot.log`
3. Подключение к интернету
4. Доступность API брокера

