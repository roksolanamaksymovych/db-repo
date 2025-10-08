from flask import Blueprint
from my_project.auth.controller.properties_controller import (
    get_all_properties, get_property_by_id, create_property, update_property, delete_property
)

property_bp = Blueprint('property', __name__)

property_bp.route('/properties', methods=['GET'])(get_all_properties)
property_bp.route('/properties/<int:property_id>', methods=['GET'])(get_property_by_id)
property_bp.route('/properties', methods=['POST'])(create_property)
property_bp.route('/properties/<int:property_id>', methods=['PUT'])(update_property)
property_bp.route('/properties/<int:property_id>', methods=['DELETE'])(delete_property)

