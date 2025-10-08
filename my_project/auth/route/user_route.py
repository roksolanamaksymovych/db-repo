from flask import Blueprint
from my_project.auth.controller.users_controller import (
    get_all_users, get_user_by_id, create_user, update_user, delete_user, get_users_with_properties
)

user_bp = Blueprint('user', __name__)

user_bp.route('/users', methods=['GET'])(get_all_users)
user_bp.route('/users/<int:user_id>', methods=['GET'])(get_user_by_id)
user_bp.route('/users', methods=['POST'])(create_user)
user_bp.route('/users/<int:user_id>', methods=['PUT'])(update_user)
user_bp.route('/users/<int:user_id>', methods=['DELETE'])(delete_user)
user_bp.route('/users_with_properties', methods=['GET'])(get_users_with_properties)
