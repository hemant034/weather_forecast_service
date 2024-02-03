from models.Role import Role as RoleModel
from models.Entity import Entity as EntityModel
from models.User import User as UserModel
from models.UserRoleMapping import UserRoleMapping as UserRoleMappingModel
from flask_sqlalchemy import SQLAlchemy

from config import *
from utils import *

import json
import csv

role_names: [str] = ['SUPERADMIN', 'ADMIN', 'USER']

def init_db(app):
    db = SQLAlchemy(app)
    db.init_app(app)

    with app.app_context():
        db.create_all()

    return db

def add_row_to_db(db, username, password, email, first_name, last_name):
    try:
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


def insert_users_to_db(db):
    csv_file_path = 'data/username.csv'
    with open(csv_file_path, newline='') as csvfile:
        # Create a CSV DictReader object
        csv_reader = csv.DictReader(csvfile)
        i = 0
        for row in csv_reader:
            if i > 0:
                username, password, full_name = row['username'], row['password'], row['full_name']
                first_name, last_name = full_name.split(" ", maxsplit=2)
                email = f'{username}@dummy.com'

                add_row_to_db(db, username, password, email, first_name, last_name)
            i+=1

def add_roles(db):
    print('Adding Roles')
    try:
        roles = [RoleModel(role_name=role_name) for role_name in role_names]
        db.session.bulk_save_objects(roles)
        db.session.commit()
    except:
        pass
    print('Roles Added!')


def add_super_admin(db):
    print('Adding Super Admin')
    try:
        super_admin_password_enc = encrypt(secret_key=secret_key, plain_text=super_admin_password)
        super_admin_user = UserModel(user_name='super_admin', user_email='super_admin@nodomain.com',
                                password=super_admin_password_enc, first_name='Super Admin', last_name='User')
        db.session.add(super_admin_user)
        db.session.commit()

        super_admin_role: RoleModel = RoleModel.get_role_by_name(role_name=role_names[0])
        super_admin_user_role_mapping = UserRoleMappingModel(user_name=super_admin_user.user_name,
                                                        role_id=super_admin_role.role_id)
        db.session.add(super_admin_user_role_mapping)
        db.session.commit()
    except Exception as e:
        pass


def prepare_db_setup(app):
    db_conn = init_db(app)
    add_roles(db_conn)
    add_super_admin(db_conn)
    insert_users_to_db(db_conn)

