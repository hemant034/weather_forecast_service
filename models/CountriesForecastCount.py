from app import db

class CountryVisit(db.Model):
    __tablename__ = 'country_visits'

    country_name = db.Column(db.String(80), primary_key=True)
    country_visit_counter = db.Column(db.Integer, default=0)
