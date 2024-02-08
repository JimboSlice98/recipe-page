import json
import os
import secrets
from datetime import timedelta

import requests
from dotenv import load_dotenv
from flask import (Flask, abort, redirect, render_template, request, session,
                   url_for)
from flask_login import (LoginManager, current_user, login_required,
                         login_user, logout_user)
from oauthlib.oauth2 import WebApplicationClient
from requests.exceptions import HTTPError, RequestException

# Configure app.py
app = Flask(__name__)

@app.route("/profile/<user_id>")
def profile(user_id):
    # URL of the microservice
    microservice_url = "http://51.11.180.99:5000/get-user-settings"

    # Make a POST request to the microservice
    response = requests.post(microservice_url, json={"user_id": user_id})

    if response.status_code == 200:
        # If the request was successful, extract data and pass to the template
        user_settings = response.json()
        return render_template("profile.html", user_settings=user_settings)
    else:
        # Handle errors or redirect as appropriate
        return "User settings not found", 404

# Load environment variables
# load_dotenv()

# # Get app's secret key so Flask_login can manipulate the session
# app.config['SECRET_KEY'] = os.environ.get("SECRETKEY")

# # Configure Flask login
# login_manager = LoginManager(app)
# login_manager.init_app(app)
# login_manager.login_view = "login"

# # Set cookie expiration
# app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=31)

# # Configure Google OAuth
# # to work on MacOS, turn off AirPlay receiver and do $ flask run --host=0.0.0.0
# # will only work on localhost
# GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
# GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
# GOOGLE_DISCOVERY_URL = (
#     "https://accounts.google.com/.well-known/openid-configuration")


# # Set up OAuth 2 client
# client = WebApplicationClient(GOOGLE_CLIENT_ID)


# # Define user_loader callback to load user obj from user id in session
# @login_manager.user_loader
# def load_user(user_id):
#     return User(id=user_id, username=get_username(user_id))


# # Retrieve Google's provider config
# # ADD ERROR HADNLING TO API CALL LATER
# def get_google_provider_config():
#     return requests.get(GOOGLE_DISCOVERY_URL).json()

@app.route("/", methods=["GET"])
def index():
    # Hardcoded user ID for demonstration
    user_id = "1"
    
    # URL of the microservice
    microservice_url = "http://51.11.180.99:5000/get-user-settings"
    
    try:
        # Make a POST request to the microservice
        response = requests.post(microservice_url, json={"user_id": user_id}, timeout=5)  # 5 seconds timeout
        
        if response.status_code == 200:
            # If the request was successful, extract data and pass to the template
            user_settings = response.json()
        else:
            # Non-200 response, use default values
            user_settings = {"user_id": user_id, "cooking_level": "Unknown", "birthday": "Unknown"}
    
    except requests.exceptions.RequestException as e:
        # Catch any requests exceptions (e.g., connection errors, timeout) and use default values
        print(f"Error contacting microservice: {e}")
        user_settings = {"user_id": user_id, "cooking_level": "Unknown", "birthday": "Unknown"}
    
    return render_template("index.html", user_settings=user_settings)

# Configure routing
@app.route("/home", methods=["GET"])
def home():
    # return index 1
    return render_template("index.html")


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404
