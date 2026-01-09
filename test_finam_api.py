#!/usr/bin/env python3
"""Скрипт для тестирования Finam API"""

import requests
import os
from pathlib import Path
from dotenv import load_dotenv

# Загрузка .env из текущей директории
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

token = os.getenv('FINAM_TOKEN')
account_id = os.getenv('FINAM_ACCOUNT_ID')

print("="*60)
print("ТЕСТИРОВАНИЕ FINAM API")
print("="*60)
print(f"Токен: {token[:20] if token else 'НЕ УКАЗАН'}...")
print(f"Счет: {account_id if account_id else 'НЕ УКАЗАН'}")

if not token:
    print("\n❌ Токен Finam не указан в .env файле!")
    exit(1)

# Тест API
url = "https://trade-api.finam.ru/api/v1/portfolio"
headers = {
    "X-Api-Key": token,
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
params = {"accountId": account_id} if account_id else {}

print(f"\nURL: {url}")
print(f"Headers: X-Api-Key={token[:20]}...")
print(f"Params: {params}")

try:
    print("\nОтправка запроса...")
    response = requests.get(url, headers=headers, params=params, timeout=10)
    
    print(f"\nСтатус ответа: {response.status_code}")
    print(f"Заголовки ответа: {dict(response.headers)}")
    
            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', '')
                
                # Проверяем, что ответ JSON, а не HTML
                if 'text/html' in content_type:
                    print(f"\n⚠️  API вернул HTML вместо JSON!")
                    print(f"Это означает, что URL неправильный или Finam использует другой формат API.")
                    print(f"\nВозможные причины:")
                    print(f"1. URL https://trade-api.finam.ru/api/v1/portfolio не существует")
                    print(f"2. Finam использует другой формат API (возможно, нужна авторизация через торговый терминал)")
                    print(f"3. Токен неверный или не имеет прав на доступ к API")
                    print(f"\nРекомендация: Используйте INITIAL_CAPITAL из настроек для работы бота.")
                    print(f"Бот будет работать, но баланс будет браться из .env файла (INITIAL_CAPITAL)")
                    print(f"\nHTML ответ (первые 500 символов):")
                    print(response.text[:500])
                else:
                    try:
                        data = response.json()
                        print(f"\n✅ Успешный ответ (JSON):")
                        print(f"Данные: {data}")
                        
                        # Попытка извлечь баланс
                        if 'totalValue' in data:
                            print(f"\n💰 Общая стоимость портфеля: {data['totalValue']}")
                        if 'cash' in data:
                            print(f"💵 Денежные средства: {data['cash']}")
                        if 'positions' in data:
                            print(f"📊 Позиций: {len(data['positions'])}")
                    except Exception as e:
                        print(f"\n⚠️  Не удалось распарсить JSON: {e}")
                        print(f"Текст ответа: {response.text[:500]}")
    else:
        print(f"\n❌ Ошибка API:")
        print(f"Текст ответа: {response.text[:500]}")
        
except requests.exceptions.RequestException as e:
    print(f"\n❌ Ошибка запроса: {e}")
except Exception as e:
    print(f"\n❌ Неожиданная ошибка: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)

