from app import db

class UserForecastVisit(db.Model):
    __tablename__ = 'user_forecast_visits'

    username = db.Column(db.String(80), primary_key=True)
    forecast_visit_counter = db.Column(db.Integer, default=0)
