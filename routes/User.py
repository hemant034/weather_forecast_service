from flask import Flask, session, request, make_response, redirect, url_for, jsonify
from flask_session import Session
from app import app, db, secret_key, getResponseHeaders
from models.HttpResponse import HttpResponse
from models.UserCount import UserVisit
import json
from services import User as user_service
from logger import logger
import jwt

app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = secret_key

Session(app)

def increment_visit_counter(username: str):
    """
    Function to increment user login counter.
    """
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
    """
    Endpoint to login to the weather forecast application.
    """
    try:
        if 'user_id' in session:
            # User is already logged in, handle accordingly
            logger.info("User is already logged in.")
            status, message, data = (400, 'Bad request', {'error': 'User is already logged in'})
        else:
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
                    logger.info(f"User {user_name} logged in successfully.")
            else:
                status, message, data = (400, 'Bad request', None)
                logger.error(f'Error logging in the user : {message}')
                
        response = HttpResponse(message=message, status=status, data=data)
    except Exception as e:
        exception_str = str(e)
        logger.error(f"Failed to login the user : {exception_str}")
        response = HttpResponse(message='Exception Occurred - ' + exception_str, status=500)

    return make_response(json.dumps(response.__dict__), response.status, getResponseHeaders())

@app.route('/logout')
def logout():
    """
    Endpoint to logout from the weather forecast application.
    """
    # Clear user user session for logging out.
    if 'user_id' not in session:
        logger.info("User has already logged out.")
        status, message, data = (400, 'Bad request', {'error': 'User already logged out.'})
    else:
        logger.info("User logged out successfully.")
        user_id = session.pop('user_id', None)
        status, message, data = (200, 'Logged out successfully.', {'user_id': user_id})
    
    response = HttpResponse(message=message, status=status, data=data)
    return make_response(json.dumps(response.__dict__), response.status, getResponseHeaders())


@app.route('/current_user')
def current_user():
    """
    Endpoint to get the current user logged in to the weather forecast application.
    """
    user_id = session.get('user_id')
    if user_id:
        # Retrieve the current user information from the database based on user_id
        user_info = session['user_id']
        message, data, status = 'User is logged in', {'username' : user_info}, 200
        logger.info(f'User {user_info} is logged in.')
    else:
        message, data, status = 'User is not logged in',{'username': None}, 401
        logger.info("User is not logged in.")
    
    response = HttpResponse(message=message, status=status, data=data)
    return make_response(json.dumps(response.__dict__), response.status, getResponseHeaders())