from my_project.auth.dao.usersdao import UserDAO

class UserService:
    def __init__(self):
        self.user_dao = UserDAO()

    def get_all_users(self):
        return self.user_dao.get_all()

    def get_user_by_id(self, user_id):
        return self.user_dao.get_by_id(user_id)

    def create_user(self, data):
        return self.user_dao.create(data)

    def update_user(self, user_id, data):
        return self.user_dao.update(user_id, data)

    def delete_user(self, user_id):
        return self.user_dao.delete(user_id)

    def get_users_with_properties(self):
        users = self.user_dao.get_all()
        result = []
        for user in users:
            result.append({
                'user_id': user.user_id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'balance': float(user.balance),
                'properties': [
                    {
                        'property_id': property_obj.property_id,
                        'title': property_obj.title,
                        'description': property_obj.description,
                        'price_per_night': float(property_obj.price_per_night),
                        'address': property_obj.address
                    } for property_obj in user.properties
                ]
            })
        return result
