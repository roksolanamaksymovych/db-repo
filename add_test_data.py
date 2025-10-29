#!/usr/bin/env python3
"""
Скрипт для додавання тестових даних через API
"""

import requests
import json
import sys

def add_test_data(base_url):
    """Додає тестові дані через REST API"""
    
    base_url = base_url.rstrip('/')
    
    print("🚀 Додавання тестових даних до API...")
    print(f"URL: {base_url}\n")
    
    # Тестові користувачі
    users = [
        {"Name": "Іван Петренко", "email": "ivan@example.com", "phone": "+380501234567"},
        {"Name": "Марія Коваленко", "email": "maria@example.com", "phone": "+380502345678"},
        {"Name": "Олексій Шевченко", "email": "oleksiy@example.com", "phone": "+380503456789"},
    ]
    
    # Тестові категорії
    categories = [
        {"CategoryName": "Електроніка", "Description": "Електронні пристрої та гаджети"},
        {"CategoryName": "Меблі", "Description": "Домашні та офісні меблі"},
        {"CategoryName": "Одяг", "Description": "Чоловічий та жіночий одяг"},
    ]
    
    # Тестові властивості
    properties = [
        {"PropertyName": "iPhone 15", "Price": 45000.00, "Description": "Новий iPhone 15", "OwnerID": 1},
        {"PropertyName": "MacBook Pro", "Price": 85000.00, "Description": "MacBook Pro M3", "OwnerID": 1},
        {"PropertyName": "Стіл офісний", "Price": 3500.00, "Description": "Ергономічний офісний стіл", "OwnerID": 2},
        {"PropertyName": "Куртка зимова", "Price": 2500.00, "Description": "Тепла зимова куртка", "OwnerID": 3},
    ]
    
    print("1️⃣ Додавання користувачів...")
    for user in users:
        try:
            response = requests.post(f"{base_url}/api/users", json=user, timeout=10)
            if response.status_code in [200, 201]:
                print(f"   ✅ Додано: {user['Name']}")
            else:
                print(f"   ⚠️  Не вдалося додати {user['Name']}: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Помилка: {e}")
    
    print("\n2️⃣ Додавання категорій...")
    for category in categories:
        try:
            response = requests.post(f"{base_url}/api/categories", json=category, timeout=10)
            if response.status_code in [200, 201]:
                print(f"   ✅ Додано: {category['CategoryName']}")
            else:
                print(f"   ⚠️  Не вдалося додати {category['CategoryName']}: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Помилка: {e}")
    
    print("\n3️⃣ Додавання властивостей...")
    for prop in properties:
        try:
            response = requests.post(f"{base_url}/api/properties", json=prop, timeout=10)
            if response.status_code in [200, 201]:
                print(f"   ✅ Додано: {prop['PropertyName']}")
            else:
                print(f"   ⚠️  Не вдалося додати {prop['PropertyName']}: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Помилка: {e}")
    
    print("\n" + "="*50)
    print("✅ Готово! Перевірте Swagger:")
    print(f"   {base_url}/api/docs/")
    print("="*50)
    
    # Перевірка даних
    print("\n4️⃣ Перевірка даних...")
    endpoints = [
        ("/api/users", "Користувачі"),
        ("/api/categories", "Категорії"),
        ("/api/properties", "Властивості"),
    ]
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                count = len(data) if isinstance(data, list) else "?"
                print(f"   ✅ {name}: {count} записів")
            else:
                print(f"   ⚠️  {name}: помилка {response.status_code}")
        except Exception as e:
            print(f"   ❌ {name}: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Використання: python3 add_test_data.py <URL>")
        print("")
        print("Приклади:")
        print("  python3 add_test_data.py http://localhost:5000")
        print("  python3 add_test_data.py https://your-app.azurecontainerapps.io")
        sys.exit(1)
    
    url = sys.argv[1]
    add_test_data(url)

