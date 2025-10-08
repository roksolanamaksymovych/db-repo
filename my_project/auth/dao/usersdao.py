from my_project.db_init import db
from my_project.auth.models.users import User

class UserDAO:
    def get_all(self):
        """Отримати всіх користувачів"""
        return User.query.all()

    def get_by_id(self, user_id):
        """Отримати користувача за ID"""
        return User.query.get(user_id)

    def create(self, data):
        """Створити нового користувача"""
        new_user = User(**data)
        db.session.add(new_user)
        db.session.commit()
        return new_user

    def update(self, user_id, data):
        """Оновити користувача за ID"""
        user = User.query.get(user_id)
        if user:
            for key, value in data.items():
                setattr(user, key, value)
            db.session.commit()
            return user
        return None

    def delete(self, user_id):
        """Видалити користувача за ID"""
        user = User.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return True
        return False
