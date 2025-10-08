from flask import Flask
from __init__ import create_app
from my_project.auth.route.user_route import user_bp
from my_project.auth.route.category_route import category_bp
from my_project.auth.route.property_route import property_bp
from my_project.auth.route.property_categories_route import property_category_bp
from dotenv import load_dotenv
import os

# Завантаження змінних середовища з .env файлу
load_dotenv()

app = create_app()

app.register_blueprint(user_bp)
app.register_blueprint(category_bp)
app.register_blueprint(property_bp)
app.register_blueprint(property_category_bp)


if __name__ == '__main__':
    # Використовуємо порт з змінної середовища або 5000 за замовчуванням
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
