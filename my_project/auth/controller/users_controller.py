from flask import request, jsonify
from my_project.auth.service.Users import UserService
from flasgger import swag_from

user_service = UserService()

# Отримати всіх користувачів
def get_all_users():
    """
    Отримати всіх користувачів
    ---
    tags:
      - Users
    responses:
      200:
        description: Список всіх користувачів
        schema:
          type: array
          items:
            type: object
            properties:
              user_id:
                type: integer
              name:
                type: string
              email:
                type: string
    """
    users = user_service.get_all_users()
    return jsonify([user.to_dict() for user in users]), 200

# Отримати користувача за ID
def get_user_by_id(user_id):
    """
    Отримати користувача за ID
    ---
    tags:
      - Users
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
        description: ID користувача
    responses:
      200:
        description: Дані користувача
        schema:
          type: object
          properties:
            user_id:
              type: integer
            name:
              type: string
            email:
              type: string
      404:
        description: Користувача не знайдено
    """
    user = user_service.get_user_by_id(user_id)
    if user:
        return jsonify(user.to_dict()), 200
    return jsonify({'message': 'User not found'}), 404

# Створити нового користувача
def create_user():
    """
    Створити нового користувача
    ---
    tags:
      - Users
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - name
            - email
          properties:
            name:
              type: string
              example: "Іван Петренко"
            email:
              type: string
              example: "ivan@example.com"
    responses:
      201:
        description: Користувача створено
        schema:
          type: object
          properties:
            user_id:
              type: integer
            name:
              type: string
            email:
              type: string
    """
    data = request.json
    new_user = user_service.create_user(data)
    return jsonify(new_user.to_dict()), 201

# Оновити користувача за ID
def update_user(user_id):
    """
    Оновити користувача за ID
    ---
    tags:
      - Users
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
        description: ID користувача
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
              example: "Оновлене ім'я"
            email:
              type: string
              example: "newemail@example.com"
    responses:
      200:
        description: Користувача оновлено
      404:
        description: Користувача не знайдено
    """
    data = request.json
    updated_user = user_service.update_user(user_id, data)
    if updated_user:
        return jsonify(updated_user.to_dict()), 200
    return jsonify({'message': 'User not found'}), 404

# Видалити користувача за ID
def delete_user(user_id):
    """
    Видалити користувача за ID
    ---
    tags:
      - Users
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
        description: ID користувача
    responses:
      200:
        description: Користувача видалено
      404:
        description: Користувача не знайдено
    """
    success = user_service.delete_user(user_id)
    if success:
        return jsonify({'message': 'User deleted successfully'}), 200
    return jsonify({'message': 'User not found'}), 404

# Отримати всіх користувачів з деталями про їх властивості
def get_users_with_properties():
    """
    Отримати всіх користувачів з властивостями
    ---
    tags:
      - Users
    responses:
      200:
        description: Список користувачів з їх властивостями
        schema:
          type: array
          items:
            type: object
    """
    users_with_properties = user_service.get_users_with_properties()
    return jsonify(users_with_properties), 200
