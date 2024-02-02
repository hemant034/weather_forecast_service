from app import db


class Role(db.Model):
    __tablename__ = 'roles'
    role_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    role_name = db.Column(db.String(255), nullable=False)

    def __init__(self, role_name):
        self.role_name = role_name

    @staticmethod
    def get_role_by_name(role_name):
        return (
            db.session.query(Role)
            .filter(Role.role_name == role_name)
            .first()
        )
