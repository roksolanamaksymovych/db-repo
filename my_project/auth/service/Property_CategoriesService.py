from my_project.auth.dao.property_categoriesdao import PropertyCategoryDAO


class PropertyCategoryService:
    def __init__(self):
        self.property_category_dao = PropertyCategoryDAO()

    def add_category_to_property(self, property_id, category_id):
        return self.property_category_dao.add_category_to_property(property_id, category_id)

    def remove_category_from_property(self, property_id, category_id):
        return self.property_category_dao.remove_category_from_property(property_id, category_id)

    def get_properties_with_categories(self):
        # Отримання даних як списку словників
        properties_with_categories = self.property_category_dao.get_properties_with_categories()

        # Перевірка на відповідність очікуваному формату
        result = []
        for property_obj in properties_with_categories:
            property_data = {
                'property_id': property_obj['property_id'],
                'title': property_obj['title'],
                'description': property_obj['description'],
                'price_per_night': float(property_obj['price_per_night']),
                'address': property_obj['address'],
                'categories': [
                    {
                        'category_id': category['category_id'],
                        'name': category['name'],
                        'description': category['description']
                    } for category in property_obj['categories']
                ]
            }
            result.append(property_data)

        return result

