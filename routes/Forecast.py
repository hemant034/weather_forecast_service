from flask import Flask, session, request, jsonify, make_response
from flask_session import Session
from app import app, db, secret_key, getResponseHeaders
from models.HttpResponse import HttpResponse
from models.UserForecastCount import UserForecastVisit
from models.CitiesForecastCount import CityVisit
from models.CountriesForecastCount import CountryVisit
from logger import logger
from config import *
import json
import requests


app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = secret_key

country_names = set()
city_country_map = dict()

try:
    with open('data/country_data.json', 'r', encoding='utf-8') as file:
        logger.info("Fetching data countries data.")
        cities_data = json.load(file)
        country_names = set([city_item['country'] for city_item in cities_data])
        city_country_map = {item['name']: item['country'] for item in cities_data}
except FileNotFoundError as e:
    logger.error(f'Failed to fetch the data from file : {str(e)}')

Session(app)

def increment_forecast_user_counter(username):
    # Check if the user exists in the user_visits table
    user_visit = UserForecastVisit.query.get(username)
    if user_visit:
        # If the user exists, increment the visit counter
        user_visit.forecast_visit_counter += 1
    else:
        # If the user doesn't exist, create a new record with the username
        new_user_visit = UserForecastVisit(username=username, forecast_visit_counter=1)
        db.session.add(new_user_visit)

    db.session.commit()

def increment_cities_forecast_counter(city_name):
    # Check if the user exists in the user_visits table
    city_visit = CityVisit.query.get(city_name)
    if city_visit:
        # If the user exists, increment the visit counter
        city_visit.city_visit_counter += 1
    else:
        # If the user doesn't exist, create a new record with the username
        new_city_visit = CityVisit(city_name=city_name, city_visit_counter=1)
        db.session.add(new_city_visit)

    db.session.commit()

def increment_countries_forecast_counter(country_name):
    # Check if the user exists in the user_visits table
    country_visit = CountryVisit.query.get(country_name)
    if country_visit:
        # If the user exists, increment the visit counter
        country_visit.country_visit_counter += 1
    else:
        # If the user doesn't exist, create a new record with the username
        new_country_visit = CountryVisit(country_name=country_name, country_visit_counter=1)
        db.session.add(new_country_visit)

    db.session.commit()

@app.route('/forecast', methods=['GET'])
def forecast_weather():
    place_name: str = request.args.get('place_name')
    days: int = request.args.get('days')
    api_key = weather_api_key
    url = f'http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={place_name}&days={days}'
    logger.info(f'Fetching forecast for {place_name}')
    try:
        user_id = session.get('user_id')
        response = requests.get(url)
        response.raise_for_status()
        json_data = response.json()
        if place_name in country_names:
            increment_countries_forecast_counter(place_name)
        elif place_name in city_country_map:
            increment_cities_forecast_counter(place_name)
            increment_countries_forecast_counter(city_country_map[place_name])
        increment_forecast_user_counter(user_id)
        message = f'Forcast for {place_name} fetched successfully'
        status = 200
        data = json_data
        logger.info(f'{message} by {user_id}.')
    except requests.exceptions.RequestException as e:
        message = f'Failed to fetch forecast for {place_name}'
        status = 500
        data = {"error": str(e)}
        logger.error(f"Failed to fetch forecast for {place_name} : {str(e)}")
    
    response = HttpResponse(message=message, status=status, data=data)
    return make_response(json.dumps(response.__dict__), response.status, getResponseHeaders()) 
    

@app.route('/forecast/top_users', methods=['GET'])
def top_users():
    try:
        # Fetch the top n users based on forecast visit counter
        n: int = request.args.get('n', 1)
        logger.info(f'Fetching top {n} users using forecast.')
        top_users = (
            db.session.query(UserForecastVisit)
            .order_by(UserForecastVisit.forecast_visit_counter.desc())
            .limit(n)
            .all()
        )

        # Prepare the response
        result = [
            {'username': user.username, 'forecast_visit_counter': user.forecast_visit_counter}
            for user in top_users
        ]
        message = f'Top {n} forecast users fetched successfully.'
        status = 200
        data = result
        logger.info(message)
    except Exception as e:
        message = f'Failed to fetch top {n} forecast users.'
        status = 500
        data = {"error": str(e)}
        logger.error(f'{message} : str(e)')
        
    response = HttpResponse(message=message, status=status, data=data)
    return make_response(json.dumps(response.__dict__), response.status, getResponseHeaders()) 
    

@app.route('/forecast/top_countries', methods=['GET'])
def top_countries():
    try:
        # Fetch the top n countries based on country visit counter
        n: int = request.args.get('n', 1)
        logger.info(f'Fetching top {n} countries forecasted.')
        top_countries = (
            db.session.query(CountryVisit)
            .order_by(CountryVisit.country_visit_counter.desc())
            .limit(n)
            .all()
        )

        # Prepare the response
        result = [
            {'country_name': country.country_name, 'country_visit_counter': country.country_visit_counter}
            for country in top_countries
        ]
        message = f'Top {n} forecasted countries fetched successfully.'
        status = 200
        data = result
        logger.info(message)
    except Exception as e:
        message = f'Failed to fetch top {n} forecasted countries.'
        status = 500
        data = {"error": str(e)}
        logger.error(f'{message} : str(e)')

    response = HttpResponse(message=message, status=status, data=data)
    return make_response(json.dumps(response.__dict__), response.status, getResponseHeaders()) 
    

@app.route('/forecast/top_cities', methods=['GET'])
def top_cities():
    try:
        n: int = request.args.get('n', 1)
        logger.info(f'Fetching top {n} cities forecasted.')
        # Fetch the top n cities based on city visit counter
        top_cities = (
            db.session.query(CityVisit)
            .order_by(CityVisit.city_visit_counter.desc())
            .limit(n)
            .all()
        )

        # Prepare the response
        result = [
            {'city_name': city.city_name, 'city_visit_counter': city.city_visit_counter}
            for city in top_cities
        ]
        message = f'Top {n} forecasted cities fetched successfully.'
        status = 200
        data = result
        logger.info(message)
    except Exception as e:
        message = f'Failed to fetch top {n} forecasted cities.'
        status = 500
        data = {"error": str(e)}
        logger.error(f'{message} : str(e)')
    
    response = HttpResponse(message=message, status=status, data=data)
    return make_response(json.dumps(response.__dict__), response.status, getResponseHeaders()) 