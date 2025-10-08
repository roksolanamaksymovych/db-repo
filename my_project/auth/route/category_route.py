from flask import Blueprint
from my_project.auth.controller.categories_controller import (
    get_all_categories, get_category_by_id, create_category, update_category, delete_category
)

category_bp = Blueprint('category', __name__)

category_bp.route('/categories', methods=['GET'])(get_all_categories)
category_bp.route('/categories/<int:category_id>', methods=['GET'])(get_category_by_id)
category_bp.route('/categories', methods=['POST'])(create_category)
category_bp.route('/categories/<int:category_id>', methods=['PUT'])(update_category)
category_bp.route('/categories/<int:category_id>', methods=['DELETE'])(delete_category)
