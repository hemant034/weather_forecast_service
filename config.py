import os


app_config_dict = {
    'SQLALCHEMY_DATABASE_URI': f'sqlite:///admin_service',
    'SQLALCHEMY_TRACK_MODIFICATIONS': True
}

secret_key = os.environ.get('secret_key', 'XYZ')
super_admin_password = os.environ.get('super_admin_password', 'ABC')
weather_api_key = os.environ.get('WEATHER_API_KEY', 'your_key')