#!/usr/bin/env python3
"""
Скрипт ініціалізації бази даних для Flask додатку
Створює всі таблиці згідно з моделями SQLAlchemy
"""

import os
import sys

# Встановлюємо змінні середовища якщо запускаємо локально
if not os.getenv('DB_HOST'):
    print("⚠️  Завантаження змінних середовища з .env файлу...")
    from dotenv import load_dotenv
    load_dotenv()

# Імпортуємо додаток
from app import app
from my_project.db_init import db

# Імпортуємо всі моделі (важливо для створення таблиць!)
from my_project.auth.models.users import User
from my_project.auth.models.category import Category
from my_project.auth.models.property import Property
from my_project.auth.models.property_categories import PropertyCategory


def init_database():
    """Ініціалізація бази даних"""
    print("=" * 60)
    print("🗄️  ІНІЦІАЛІЗАЦІЯ БАЗИ ДАНИХ")
    print("=" * 60)
    
    with app.app_context():
        try:
            # Отримуємо інформацію про підключення
            db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
            # Приховуємо пароль у виводі
            safe_uri = db_uri.split('@')[1] if '@' in db_uri else 'localhost'
            print(f"\n📡 Підключення до: {safe_uri}")
            
            # Видалення всіх таблиць (обережно! Видаляє всі дані)
            print("\n⚠️  Видалення існуючих таблиць...")
            db.drop_all()
            print("✅ Старі таблиці видалено")
            
            # Створення всіх таблиць
            print("\n🔨 Створення нових таблиць...")
            db.create_all()
            print("✅ Таблиці створено успішно!")
            
            # Показуємо які таблиці створено
            print("\n📋 Створені таблиці:")
            tables = [
                "  • users (користувачі)",
                "  • categories (категорії)",
                "  • properties (властивості)",
                "  • property_categories (зв'язок властивостей і категорій)"
            ]
            for table in tables:
                print(table)
            
            # Опціонально: додати тестові дані
            print("\n" + "=" * 60)
            add_test = input("Додати тестові дані? (y/n): ").lower()
            
            if add_test == 'y':
                add_sample_data()
            
            print("\n" + "=" * 60)
            print("✅ ІНІЦІАЛІЗАЦІЯ ЗАВЕРШЕНА УСПІШНО!")
            print("=" * 60)
            print("\n🚀 Тепер можна запустити додаток:")
            print("   python app.py")
            print("\n📖 Swagger документація буде доступна:")
            print("   http://localhost:5000/api/docs/")
            print("\n")
            
        except Exception as e:
            print(f"\n❌ ПОМИЛКА: {e}")
            print("\n💡 Перевірте:")
            print("  1. Чи правильні дані підключення в .env файлі")
            print("  2. Чи доступний MySQL сервер")
            print("  3. Чи існує база даних")
            sys.exit(1)


def add_sample_data():
    """Додати тестові дані"""
    print("\n📝 Додавання тестових даних...")
    
    try:
        # Створюємо тестового користувача
        test_user = User(
            username="Іван Петренко",
            email="ivan@example.com",
            password="hashed_password_123",  # В реальності має бути захешований
            role="owner",
            balance=1000.00
        )
        db.session.add(test_user)
        
        # Створюємо тестові категорії
        category1 = Category(
            name="Квартири",
            description="Квартири для оренди"
        )
        category2 = Category(
            name="Будинки",
            description="Приватні будинки"
        )
        db.session.add_all([category1, category2])
        
        # Зберігаємо щоб отримати ID
        db.session.commit()
        
        # Створюємо тестову властивість
        test_property = Property(
            owner_id=test_user.user_id,
            title="Затишна квартира в центрі",
            description="Прекрасна квартира з видом на парк",
            price_per_night=500.00,
            address="вул. Хрещатик, 1, Київ"
        )
        db.session.add(test_property)
        db.session.commit()
        
        # Зв'язуємо властивість з категорією
        prop_cat = PropertyCategory(
            property_id=test_property.property_id,
            category_id=category1.category_id
        )
        db.session.add(prop_cat)
        db.session.commit()
        
        print("✅ Тестові дані додано:")
        print(f"  • Користувач: {test_user.username}")
        print(f"  • Категорії: {category1.name}, {category2.name}")
        print(f"  • Властивість: {test_property.title}")
        
    except Exception as e:
        db.session.rollback()
        print(f"⚠️  Помилка при додаванні тестових даних: {e}")


if __name__ == "__main__":
    init_database()

