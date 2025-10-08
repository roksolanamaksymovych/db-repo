from my_project.auth.dao.categoriesdao import CategoryDAO

class CategoryService:
    def __init__(self):
        self.category_dao = CategoryDAO()

    def get_all_categories(self):
        return self.category_dao.get_all()

    def get_category_by_id(self, category_id):
        return self.category_dao.get_by_id(category_id)

    def create_category(self, data):
        return self.category_dao.create(data)

    def update_category(self, category_id, data):
        return self.category_dao.update(category_id, data)

    def delete_category(self, category_id):
        return self.category_dao.delete(category_id)
