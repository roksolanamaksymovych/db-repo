from flask import request, jsonify
from my_project.auth.service.Property_CategoriesService import PropertyCategoryService

property_category_service = PropertyCategoryService()

# Додати категорію до властивості
def add_category_to_property(property_id):
    data = request.json
    category_id = data.get("category_id")
    if not category_id:
        return jsonify({"message": "Category ID is required"}), 400

    success = property_category_service.add_category_to_property(property_id, category_id)
    if success:
        return jsonify({"message": "Category added to property successfully"}), 201
    return jsonify({"message": "Failed to add category to property"}), 400

# Видалити категорію з властивості
def remove_category_from_property(property_id, category_id):
    success = property_category_service.remove_category_from_property(property_id, category_id)
    if success:
        return jsonify({"message": "Category removed from property successfully"}), 200
    return jsonify({"message": "Failed to remove category from property"}), 400

# Отримати всі властивості з їх категоріями
def get_properties_with_categories():
    properties_with_categories = property_category_service.get_properties_with_categories()
    return jsonify(properties_with_categories), 200
