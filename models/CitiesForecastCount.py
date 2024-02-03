from app import db

class CityVisit(db.Model):
    __tablename__ = 'city_visits'

    city_name = db.Column(db.String(80), primary_key=True)
    city_visit_counter = db.Column(db.Integer, default=0)
