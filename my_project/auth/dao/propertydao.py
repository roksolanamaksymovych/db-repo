from my_project.db_init import db
from my_project.auth.models.property import Property

class PropertyDAO:
    def get_all(self):
        return Property.query.all()

    def get_by_id(self, property_id):
        return Property.query.get(property_id)

    def create(self, data):
        new_property = Property(**data)
        db.session.add(new_property)
        db.session.commit()
        return new_property

    def update(self, property_id, data):
        property_obj = Property.query.get(property_id)
        if property_obj:
            for key, value in data.items():
                setattr(property_obj, key, value)
            db.session.commit()
            return property_obj
        return None

    def delete(self, property_id):
        property_obj = Property.query.get(property_id)
        if property_obj:
            db.session.delete(property_obj)
            db.session.commit()
            return True
        return False
