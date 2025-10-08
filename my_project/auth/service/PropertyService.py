from my_project.auth.dao.propertydao import PropertyDAO

class PropertyService:
    def __init__(self):
        self.property_dao = PropertyDAO()

    def get_all_properties(self):
        return self.property_dao.get_all()

    def get_property_by_id(self, property_id):
        return self.property_dao.get_by_id(property_id)

    def create_property(self, data):
        return self.property_dao.create(data)

    def update_property(self, property_id, data):
        return self.property_dao.update(property_id, data)

    def delete_property(self, property_id):
        return self.property_dao.delete(property_id)

    def get_properties_with_categories(self):
        properties = self.property_dao.get_all()
        result = []
        for property_obj in properties:
            result.append({
                'property_id': property_obj.property_id,
                'title': property_obj.title,
                'description': property_obj.description,
                'price_per_night': float(property_obj.price_per_night),
                'address': property_obj.address,
                'categories': [
                    {
                        'category_id': category.category_id,
                        'name': category.name,
                        'description': category.description
                    } for category in property_obj.categories
                ]
            })
        return result
