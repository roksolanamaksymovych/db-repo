from flask import request, jsonify
from my_project.auth.service.PropertyService import PropertyService

property_service = PropertyService()

# Отримати всі властивості
def get_all_properties():
    properties = property_service.get_all_properties()
    return jsonify([property.to_dict() for property in properties]), 200

# Отримати властивість за ID
def get_property_by_id(property_id):
    property = property_service.get_property_by_id(property_id)
    if property:
        return jsonify(property.to_dict()), 200
    return jsonify({'message': 'Property not found'}), 404

# Створити нову властивість
def create_property():
    data = request.json
    new_property = property_service.create_property(data)
    return jsonify(new_property.to_dict()), 201

# Оновити властивість за ID
def update_property(property_id):
    data = request.json
    updated_property = property_service.update_property(property_id, data)
    if updated_property:
        return jsonify(updated_property.to_dict()), 200
    return jsonify({'message': 'Property not found'}), 404

# Видалити властивість за ID
def delete_property(property_id):
    success = property_service.delete_property(property_id)
    if success:
        return jsonify({'message': 'Property deleted successfully'}), 200
    return jsonify({'message': 'Property not found'}), 404
