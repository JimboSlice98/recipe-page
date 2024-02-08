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


# Configure routing
@app.route("/", methods=["GET"])
def index():
    # return index
    return render_template("index.html")


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404
