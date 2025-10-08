from my_project.db_init import db

class Property(db.Model):
    __tablename__ = 'properties'

    property_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price_per_night = db.Column(db.Numeric(10, 2), nullable=False)
    address = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.TIMESTAMP, nullable=False, server_default=db.func.current_timestamp())

    # Зв’язок з таблицею Users (власник)
    owner = db.relationship('User', back_populates='properties')

    # Зв’язок через стикувальну таблицю PropertyCategories
    categories = db.relationship('PropertyCategory', back_populates='property', cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'property_id': self.property_id,
            'title': self.title,
            'description': self.description,
            'price_per_night': float(self.price_per_night),
            'address': self.address,
            'created_at': self.created_at.isoformat()
        }
