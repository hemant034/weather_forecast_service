from flask import Flask, session, request, make_response, redirect, url_for, jsonify
from flask_session import Session
from app import app, db, secret_key, getResponseHeaders
from models.HttpResponse import HttpResponse
from models.UserCount import UserVisit
import json
from services import User as user_service
import jwt

app.config['SESSION_TYPE'] = 'filesystem'  # You can use other session types as well
app.config['SECRET_KEY'] = secret_key

Session(app)

def increment_visit_counter(username):
    # Check if the user exists in the user_visits table
    user_visit = UserVisit.query.get(username)
    if user_visit:
        # If the user exists, increment the visit counter
        user_visit.visit_counter += 1
    else:
        # If the user doesn't exist, create a new record with the username
        new_user_visit = UserVisit(username=username, visit_counter=1)
        db.session.add(new_user_visit)

    db.session.commit()

@app.route('/login', methods=['POST'])
def login():
    try:
        # Cleanup stale session if present.
        session.pop('user_id', None)

        payload: dict = request.json
        user_name: str = payload.get('user_name', None)
        password: str = payload.get('password', None)
        if user_name and password:
            status, message, data = user_service.validate_user_credentials(user_name=user_name, password=password)
            if status == 200:
                # Store user session info.
                session['user_id'] = data.get('user_name')
                access_token = jwt.encode(payload=data, key=secret_key, algorithm='HS256')
                data['access_token'] = access_token

                # Increment the user visit counter for analytics.
                increment_visit_counter(user_name)
        else:
            status, message, data = (400, 'Bad request', None)

        response = HttpResponse(message=message, status=status, data=data)
    except Exception as e:
        exception_str = str(e)
        response = HttpResponse(message='Exception Occurred - ' + exception_str, status=500)

    return make_response(json.dumps(response.__dict__), response.status, getResponseHeaders())

@app.route('/logout')
def logout():
    # Clear user user session for logging out.
    session.pop('user_id', None)
    return {'msg' : 'Logged out!'} 


@app.route('/current_user')
def current_user():
    user_id = session.get('user_id')
    if user_id:
        # Retrieve the current user information from the database based on user_id
        user_info = session['user_id']
        return jsonify(user_info)
    else:
        return jsonify({'message': 'User not logged in'}), 401

