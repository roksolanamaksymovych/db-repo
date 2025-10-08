from my_project.db_init import db
from my_project.auth.models.category import Category

class CategoryDAO:
    def get_all(self):
        return Category.query.all()

    def get_by_id(self, category_id):
        return Category.query.get(category_id)

    def create(self, data):
        new_category = Category(**data)
        db.session.add(new_category)
        db.session.commit()
        return new_category

    def update(self, category_id, data):
        category = Category.query.get(category_id)
        if category:
            for key, value in data.items():
                setattr(category, key, value)
            db.session.commit()
            return category
        return None

    def delete(self, category_id):
        category = Category.query.get(category_id)
        if category:
            db.session.delete(category)
            db.session.commit()
            return True
        return False
