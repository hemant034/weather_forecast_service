from flask import Blueprint, jsonify
import json

country_bp = Blueprint('country_bp', __name__)


@country_bp.route('/', methods=['GET'])
def list_countries():
    try:
        with open('data/country_data.json', 'r', encoding='utf-8') as file:
            cities_data = json.load(file)
            country_names = list(set([city_item['country'] for city_item in cities_data]))
            return jsonify(sorted(country_names))
    except FileNotFoundError:
        return jsonify({"error": "Country data file not found"}), 500
    
@country_bp.route('/cities/<country_name>', methods=['GET'])
def list_cities(country_name):
    city_list = []
    try:
        with open('data/country_data.json', 'r', encoding='utf-8') as file:
            cities_data = json.load(file)
            for city_data in cities_data:
                if city_data['country'] == country_name:
                    city_list.append(city_data['name'])
            if not city_list:
                return jsonify({"error": "Country not found"}), 404
            return jsonify(sorted(city_list))
    except FileNotFoundError:
        return jsonify({"error": "Country data file not found"}), 500