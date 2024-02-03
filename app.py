from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

from config import *
from utils import *


import json
import csv

app = Flask(__name__)


app.config.update(app_config_dict)
CORS(app)

db = SQLAlchemy(app)
db.init_app(app)

role_names: [str] = ['SUPERADMIN', 'ADMIN', 'USER']

from models.Role import Role as RoleModel
from models.Entity import Entity as EntityModel
from models.User import User as UserModel
from models.UserRoleMapping import UserRoleMapping as UserRoleMappingModel
from models.CitiesForecastCount import CityVisit
from models.CountriesForecastCount import CountryVisit
from models.UserCount import UserVisit
from models.UserForecastCount import UserForecastVisit


from routes import User, Country, Forecast

def clear_all_data():
    # Get all tables in the database
    tables = db.metadata.tables.keys()

    # Iterate through tables and delete all data
    for table_name in tables:
        table = db.metadata.tables[table_name]
        db.session.execute(table.delete())

    # Commit the changes
    db.session.commit()

with app.app_context():
    db.create_all()

def add_row_to_db(username, password, email, first_name, last_name):
    try:
        existing_user = UserModel.query.filter_by(user_name=username).first()
        if existing_user:
            return
        
        user_password_enc = encrypt(secret_key=secret_key, plain_text=password)
        user_obj = UserModel(user_name=username, user_email=email,
                                password=user_password_enc, first_name=first_name, last_name=last_name)
        db.session.add(user_obj)
        db.session.commit()
        user_role: RoleModel = RoleModel.get_role_by_name(role_name=role_names[2])
        user_role_mapping = UserRoleMappingModel(user_name=user_obj.user_name,
                                                        role_id=user_role.role_id)
        db.session.add(user_role_mapping)
        db.session.commit()
    except Exception as e:
        print(e)

def insert_users_to_db():
    csv_file_path = 'data/username.csv'
    with open(csv_file_path, newline='') as csvfile:
        # Create a CSV DictReader object
        csv_reader = csv.DictReader(csvfile)
        i = 0
        for row in csv_reader:
            if i >= 0:
                username, password, full_name = row['username'], row['password'], row['full_name']
                first_name, last_name = full_name.split(" ", maxsplit=2)
                email = f'{username}@dummy.com'

                add_row_to_db(username, password, email, first_name, last_name)
            i+=1

    print('Users added.')


def add_roles():
    print('Adding Roles')
    try:
        for role_name in role_names:
            existing_role = RoleModel.query.filter_by(role_name=role_name).first()
            if existing_role:
                print(f"Role '{role_name}' already exists in the database.")
                continue

            new_role = RoleModel(role_name=role_name)
            db.session.add(new_role)
        
        db.session.commit()
        print('Roles Added!')
    except Exception as e:
        print(f"Error adding roles: {e}")


def add_super_admin():
    print('Adding Super Admin')
    try:
        super_admin_username = 'super_admin'
        existing_admin = UserModel.query.filter_by(user_name=super_admin_username).first()
        if existing_admin:
            print(f"Super Admin '{super_admin_username}' already exists in the database.")
            return

        super_admin_password_enc = encrypt(secret_key=secret_key, plain_text=super_admin_password)
        super_admin_user = UserModel(user_name=super_admin_username, user_email='super_admin@nodomain.com',
                                     password=super_admin_password_enc, first_name='Super Admin', last_name='User')
        db.session.add(super_admin_user)
        db.session.commit()

        super_admin_role = RoleModel.get_role_by_name(role_name=role_names[0])
        super_admin_user_role_mapping = UserRoleMappingModel(user_name=super_admin_user.user_name,
                                                              role_id=super_admin_role.role_id)
        db.session.add(super_admin_user_role_mapping)
        db.session.commit()

        print(f"Super Admin '{super_admin_username}' added to the database.")
    except Exception as e:
        print(f"Error adding Super Admin: {e}")


def add_admin_users():
    pass


def init_db(cleanup_db=False):
    if cleanup_db:
        clear_all_data()
    add_roles()
    add_super_admin()
    insert_users_to_db()
    
init_db(True)

@app.route('/')
def ping():  # put application's code here
    return 'pong'


if __name__ == '__main__':
    app.run()
