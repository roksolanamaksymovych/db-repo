from flask import Blueprint
from my_project.auth.controller.property_categories_controller import (
    add_category_to_property, remove_category_from_property, get_properties_with_categories
)

property_category_bp = Blueprint('property_category', __name__)

# Додавання категорії до властивості
property_category_bp.route('/properties/<int:property_id>/categories', methods=['POST'])(add_category_to_property)

# Видалення категорії з властивості
property_category_bp.route('/properties/<int:property_id>/categories/<int:category_id>', methods=['DELETE'])(remove_category_from_property)

# Отримати всі властивості з категоріями
property_category_bp.route('/properties_with_categories', methods=['GET'])(get_properties_with_categories)
