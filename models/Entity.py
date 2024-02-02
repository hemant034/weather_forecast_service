from app import db


class Entity(db.Model):
    __tablename__ = 'entities'
    entity_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    entity_name = db.Column(db.String(255), nullable=False)

    def __init__(self, entity_name):
        self.entity_name = entity_name
