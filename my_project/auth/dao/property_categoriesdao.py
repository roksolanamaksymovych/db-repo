from my_project.db_init import db
from my_project.auth.models.property_categories import PropertyCategory
from my_project.auth.models.property import Property
from my_project.auth.models.category import Category

class PropertyCategoryDAO:
    def get_all(self):
        return PropertyCategory.query.all()

    def add_category_to_property(self, property_id, category_id):
        new_property_category = PropertyCategory(property_id=property_id, category_id=category_id)
        db.session.add(new_property_category)
        db.session.commit()
        return new_property_category

    def remove_category_from_property(self, property_id, category_id):
        property_category = PropertyCategory.query.filter_by(property_id=property_id, category_id=category_id).first()
        if property_category:
            db.session.delete(property_category)
            db.session.commit()
            return True
        return False

    def get_properties_with_categories(self):
        # Виконує JOIN-запит для отримання властивостей з їх категоріями
        results = db.session.query(Property).outerjoin(Property.categories).all()

        properties_with_categories = []
        for property_obj in results:
            property_data = {
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
            }
            properties_with_categories.append(property_data)

        return properties_with_categories
