from flask import Flask
from my_project.db_init import db
from flasgger import Swagger
import os


def create_app():
    app = Flask(__name__)

    # Конфігурація бази даних з підтримкою змінних середовища
    db_user = os.getenv('DB_USER', 'root')
    db_password = os.getenv('DB_PASSWORD', 'Maks_mia3')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_name = os.getenv('DB_NAME', 'database_lab1_eer')
    
    # Для Azure MySQL потрібно додати SSL параметри
    if 'azure.com' in db_host or 'mysql.database.azure.com' in db_host:
        # Azure MySQL вимагає SSL, але вимикаємо перевірку сертифіката
        app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}?ssl_verify_cert=false&ssl_verify_identity=false'
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Налаштування Swagger
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/apispec.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/api/docs/"
    }
    
    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "Database Project API",
            "description": "API для управління користувачами, категоріями та властивостями",
            "version": "1.0.0",
            "contact": {
                "name": "API Support"
            }
        },
        "basePath": "/",
        "schemes": [
            "http",
            "https"
        ],
    }
    
    Swagger(app, config=swagger_config, template=swagger_template)

    return app
