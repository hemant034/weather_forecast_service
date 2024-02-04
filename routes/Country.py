from flask import Flask, session, request, make_response, redirect, url_for, jsonify
from flask_session import Session
from app import app, db, secret_key, getResponseHeaders
from models.HttpResponse import HttpResponse
from models.UserCount import UserVisit
from models.CountriesForecastCount import CountryVisit
from logger import logger
import json
from services import User as user_service

app.config['SESSION_TYPE'] = 'filesystem'  # You can use other session types as well
app.config['SECRET_KEY'] = secret_key

Session(app)

def increment_countries_visit_counter(country: str):
    # Check if the user exists in the user_visits table
    country_visit = CountryVisit.query.get(country)
    if country_visit:
        # If the user exists, increment the visit counter
        country_visit.visit_counter += 1
    else:
        # If the user doesn't exist, create a new record with the username
        new_country_visit = CountryVisit(country_name=country, visit_counter=1)
        db.session.add(new_country_visit)

    db.session.commit()

@app.route('/countries', methods=['GET'])
def list_countries():
    logger.info("Fetching list of countries.")
    try:
        with open('data/country_data.json', 'r', encoding='utf-8') as file:
            cities_data = json.load(file)
            country_names = list(set([city_item['country'] for city_item in cities_data]))
            message = "Fetched list of countries successfully."
            status = 200
            data = jsonify(sorted(country_names))
            logger.info(message)
    except FileNotFoundError as e:
        message = "Faild to fetch list of countries."
        status = 500
        data = {'error': str(e)}
        logger.error(f'{message} : str(e)')

    response = HttpResponse(message=message, status=status, data=data)
    return make_response(json.dumps(response.__dict__), response.status, getResponseHeaders())
    
    
@app.route('/cities', methods=['GET'])
def list_cities(country_name):
    country_name: str = request.args.get('country_name')
    city_list = []
    logger.info(f'Fetching list of cities for {country_name}.')
    try:
        with open('data/country_data.json', 'r', encoding='utf-8') as file:
            cities_data = json.load(file)
            for city_data in cities_data:
                if city_data['country'] == country_name:
                    city_list.append(city_data['name'])
            if not city_list:
                return jsonify({"error": "Country not found"}), 404
            message = f'Fetched list of cities for {country_name} successfully.'
            status = 200
            data = jsonify(sorted(city_list))
            logger.info(message)
    except FileNotFoundError as e:
        message = f'Failed to fetch cities for {country_name}'
        status = 500
        data = {'error' : str(e)}
        logger.error(f'{message} : str(e)')
    
    response = HttpResponse(message=message, status=status, data=data)
    return make_response(json.dumps(response.__dict__), response.status, getResponseHeaders())