from my_project.db_init import db

class Category(db.Model):
    __tablename__ = 'categories'

    category_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)

    # Зв’язок через стикувальну таблицю PropertyCategories
    properties = db.relationship('PropertyCategory', back_populates='category', cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'category_id': self.category_id,
            'name': self.name,
            'description': self.description,
            'properties': [property.to_dict() for property in self.properties]
       }
