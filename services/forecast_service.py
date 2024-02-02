from flask import Blueprint, jsonify, request
import json
import requests


forecast_bp = Blueprint('forecast_bp', __name__)

@forecast_bp.route('/', methods=['GET'])
def list_countries():
    api_key = ""
    city = "London"

    city = request.args.get('city', 'London')  # Get the 'city' parameter from the query string, defaulting to 'London'
    days = request.args.get('days', 3)  # Get the 'days' parameter from the query string, defaulting to 3

    url = f'http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={city}&days={days}'

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for 4xx or 5xx errors

        json_data = response.json()
        return jsonify(json_data)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500