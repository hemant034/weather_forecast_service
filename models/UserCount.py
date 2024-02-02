from app import db

class UserVisit(db.Model):
    __tablename__ = 'user_visits'

    username = db.Column(db.String(80), primary_key=True)
    visit_counter = db.Column(db.Integer, default=0)
