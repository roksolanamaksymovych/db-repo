from flask import Flask
from __init__ import create_app
from my_project.auth.route.user_route import user_bp
from my_project.auth.route.category_route import category_bp
from my_project.auth.route.property_route import property_bp
from my_project.auth.route.property_categories_route import property_category_bp
from dotenv import load_dotenv
import os

load_dotenv()

app = create_app()

app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(category_bp, url_prefix='/api')
app.register_blueprint(property_bp, url_prefix='/api')
app.register_blueprint(property_category_bp, url_prefix='/api')


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
