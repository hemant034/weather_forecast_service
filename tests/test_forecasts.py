import os
import unittest
from flask import Flask
from flask_testing import TestCase
from app import app, db  # Assuming your app instance and database are defined in app/__init__.py
from models.UserForecastCount import UserForecastVisit
from models.CitiesForecastCount import CityVisit
from models.CountriesForecastCount import CountryVisit
from models.Role import Role
from models.User import User
from models.UserRoleMapping import UserRoleMapping
from config import app_config_dict, weather_api_key

class TestForecastEndpoint(TestCase):
    def create_app(self):
        # Use a test configuration for the Flask app
        app.config.update(app_config_dict)
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use an in-memory SQLite database
        return app

    def setUp(self):
        # Create all tables.
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        # Drop all tables after each test
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_forecast_endpoint(self):
        # Set the Weather API key for testing
        os.environ['WEATHER_API_KEY'] = weather_api_key

        # Mock a user session
        with self.client.session_transaction() as session:
            session['user_id'] = 'test_user'

        # Make a request to the /forecast endpoint
        response = self.client.get('/forecast?place_name=Mumbai&days=3')

        # Check if the response status code is 200
        self.assertEqual(response.status_code, 200)

        # Check if the forecast counters are incremented in the database
        with self.app.app_context():
            user_visit = UserForecastVisit.query.get('test_user')
            city_visit = CityVisit.query.get('Mumbai')
            country_visit = CountryVisit.query.get('India')

            self.assertIsNotNone(user_visit)
            self.assertEqual(user_visit.forecast_visit_counter, 1)

            self.assertIsNotNone(city_visit)
            self.assertEqual(city_visit.city_visit_counter, 1)

            self.assertIsNotNone(country_visit)
            self.assertEqual(country_visit.country_visit_counter, 1)

if __name__ == '__main__':
    unittest.main()
