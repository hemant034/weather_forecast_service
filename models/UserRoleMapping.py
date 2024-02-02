from app import db


class UserEntityMapping(db.Model):
    __tablename__ = 'user_entities_mapping'
    user_name = db.Column(db.String(255), db.ForeignKey('users'), primary_key=True)
    entity_id = db.Column(db.Integer, db.ForeignKey('entities'), primary_key=True)

    def __init__(self, user_name, entity_id):
        self.user_name = user_name
        self.entity_id = entity_id


class UserRoleMapping(db.Model):
    __tablename__ = 'user_roles_mapping'
    user_name = db.Column(db.String(255), db.ForeignKey('users'), primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles'), primary_key=True)

    def __init__(self, user_name, role_id):
        self.user_name = user_name
        self.role_id = role_id
