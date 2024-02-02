import os


app_config_dict = {
    'SQLALCHEMY_DATABASE_URI': f'sqlite:///admin_service',
    'SQLALCHEMY_TRACK_MODIFICATIONS': True
}

secret_key = os.environ.get('secret_key', 'FT8H9ylGnZcfhCI5SX7Q2VL46IZd1vL1')
super_admin_password = os.environ.get('super_admin_password', 'ouC2gAbhsO')