from flask import request, jsonify
from my_project.auth.service.CategoryService import CategoryService

category_service = CategoryService()

# Отримати всі категорії
def get_all_categories():
    categories = category_service.get_all_categories()
    return jsonify([category.to_dict() for category in categories]), 200

# Отримати категорію за ID
def get_category_by_id(category_id):
    category = category_service.get_category_by_id(category_id)
    if category:
        return jsonify(category.to_dict()), 200
    return jsonify({'message': 'Category not found'}), 404

# Створити нову категорію
def create_category():
    data = request.json
    new_category = category_service.create_category(data)
    return jsonify(new_category.to_dict()), 201

# Оновити категорію за ID
def update_category(category_id):
    data = request.json
    updated_category = category_service.update_category(category_id, data)
    if updated_category:
        return jsonify(updated_category.to_dict()), 200
    return jsonify({'message': 'Category not found'}), 404

# Видалити категорію за ID
def delete_category(category_id):
    success = category_service.delete_category(category_id)
    if success:
        return jsonify({'message': 'Category deleted successfully'}), 200
    return jsonify({'message': 'Category not found'}), 404
