#!/bin/bash

# Startup script для Azure App Service

# Встановлення залежностей
pip install -r requirements.txt

# Запуск gunicorn
gunicorn --bind=0.0.0.0:8000 --timeout 600 app:app

