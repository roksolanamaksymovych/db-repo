from my_project.db_init import db

class PropertyCategory(db.Model):
    __tablename__ = 'property_categories'

    property_category_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.property_id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id'), nullable=False)

    # Відношення до Property та Category
    property = db.relationship('Property', back_populates='categories')
    category = db.relationship('Category', back_populates='properties')

    def to_dict(self):
        return {
            'property_category_id': self.property_category_id,
            'property_id': self.property_id,
            'category_id': self.category_id
        }
