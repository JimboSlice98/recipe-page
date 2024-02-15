import json
import os
import secrets
from datetime import timedelta

import requests
from dotenv import load_dotenv
from flask import (Flask, abort, redirect, render_template, request, session,
                   url_for)
# from flask_login import (LoginManager, current_user, login_required,                          login_user, logout_user)
# from oauthlib.oauth2 import WebApplicationClient
from requests.exceptions import HTTPError, RequestException

# Configure app.py
app = Flask(__name__)

# @app.route("/profile/<user_id>")
# def profile(user_id):
#     # URL of the microservice
#     microservice_url = "http://51.11.180.99:5000/get-user-settings"

#     # Make a POST request to the microservice
#     response = requests.post(microservice_url, json={"user_id": user_id})

#     if response.status_code == 200:
#         # If the request was successful, extract data and pass to the template
#         user_settings = response.json()
#         return render_template("profile.html", user_settings=user_settings)
#     else:
#         # Handle errors or redirect as appropriate
#         return "User settings not found", 404

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
    user_id = 2  # The user ID you want to fetch settings for
    # url = 'http://20.108.67.30:5000/get-user-settings'
    url = 'http://dnsawdrsseusersettings.uksouth.azurecontainer.io:5000/get-user-settings'
    
    try:
        response = requests.get(url, params={"user_id": str(user_id)})
        if response.status_code == 200:
            data = response.json()
                    
            if data:
                profile = data[0]
                return render_template("index.html", profile=profile)
            else:            
                return render_template("index.html", error="User not found")
        else:
            return render_template("index.html", error=f"Failed to fetch user settings. Status code: {response.status_code}")
    
    except requests.exceptions.RequestException as e:
        return render_template("index.html", error=str(e))
    except ValueError as e:
        return render_template("index.html", error="Failed to decode JSON from response")



blog_data = {
    'blog_id1232': {
        'blog_name': 'Amazing Lasagna Recipe',
        'user_id': 'user233',
        'recipe_ingredients': '1 tomato, 2 cups of flour, 3 eggs, 4 cups of cheese, 5 leaves of basil',
        'recipe_steps': '1. Slice the tomato, 2. Mix flour and eggs, 3. Layer the ingredients, 4. Bake for 45 minutes'
    },
    'blog_id1233': {
        'blog_name': 'Classic Chicken Parmesan',
        'user_id': '2',
        'recipe_ingredients': '2 chicken breasts, 1 cup breadcrumbs, 1 egg, 2 cups marinara sauce',
        'recipe_steps': '1. Bread the chicken, 2. Fry until golden, 3. Top with sauce and cheese, 4. Bake to melt cheese'
    },
    'blog_id1234': {
        'blog_name': 'Vegetarian Stir Fry Extravaganza',
        'user_id': '2',
        'recipe_ingredients': '1 bell pepper, 100g tofu, 2 tbsp soy sauce, 1 cup broccoli',
        'recipe_steps': '1. Chop vegetables and tofu, 2. Stir fry with soy sauce, 3. Serve over rice'
    },
    'blog_id1235': {
        'blog_name': 'Ultimate Chocolate Cake',
        'user_id': '1',
        'recipe_ingredients': '200g chocolate, 100g butter, 3 eggs, 150g sugar, 100g flour',
        'recipe_steps': '1. Melt chocolate and butter, 2. Mix in eggs and sugar, 3. Fold in flour, 4. Bake for 30 minutes'
    },
    'blog_id1236': {
        'blog_name': 'Healthy Kale Smoothie',
        'user_id': '1',
        'recipe_ingredients': '2 cups kale, 1 banana, 1 apple, 1 cup almond milk',
        'recipe_steps': '1. Chop fruits, 2. Blend with kale and almond milk until smooth'
    }
}

comment_data = {
    'blog_id1232': {
        'comment2343243': {'user_id': '2', 'comment_string': 'Wow, I love this lasagna recipe!'},
        'comment2343244': {'user_id': 'user455', 'comment_string': 'This looks absolutely delicious!'}
    },
    'blog_id1233': {
        'comment2343245': {'user_id': 'user233', 'comment_string': 'Chicken Parmesan is my favorite. Thanks for sharing!'},
        'comment2343246': {'user_id': 'user454', 'comment_string': 'I must try this over the weekend.'}
    },
    'blog_id1234': {
        'comment2343247': {'user_id': 'user455', 'comment_string': 'Love a good stir fry. This vegetarian version sounds great!'},
        'comment2343248': {'user_id': 'user233', 'comment_string': 'Tofu and soy sauce is a match made in heaven.'}
    },
    'blog_id1235': {
        'comment2343249': {'user_id': 'user455', 'comment_string': 'Chocolate cake is my weakness. Can’t wait to bake this.'},
        'comment2343250': {'user_id': 'user236', 'comment_string': 'Yum! Saving this recipe for later.'}
    },
    'blog_id1236': {
        'comment2343251': {'user_id': 'user235', 'comment_string': 'Kale and apple is such a refreshing combination!'},
        'comment2343252': {'user_id': 'user236', 'comment_string': 'Healthy and delicious. Perfect for a quick breakfast.'}
    }
}

def filter_blogs_by_user(user_id, blog_data):
    user_id = str(user_id)
    filtered_blogs = {}
    blog_ids = []
    for blog_id, data in blog_data.items():
        if data['user_id'] == user_id:
            filtered_blogs[blog_id] = data
            blog_ids.append(blog_id)
    return filtered_blogs, blog_ids

def filter_comments_by_blog_ids(blog_ids, comment_data):
    filtered_comments = {}
    for blog_id in blog_ids:
        if blog_id in comment_data:
            filtered_comments[blog_id] = comment_data[blog_id]
    return filtered_comments

def fetch_data_from_microservice(url, user_id):
    try:
        response = requests.get(url, params={"user_id": str(user_id)})
        response_code = response.status_code
        
        if response_code == 200:
            data = response.json()
            return response_code, None, data
        else:
            return response_code, f"Failed to fetch user settings. Status code: {response_code}", {}

    except requests.exceptions.RequestException as e:
        return None, str(e), {}
    except ValueError as e:
        return None, "Failed to decode JSON from response", {}
    
def fetch_user_settings(user_id):
    # url = 'http://dnsawdrsseusersettings.uksouth.azurecontainer.io:5000/get-user-settings'
    url = 'http://dnsawdrsseuserdetails.uksouth.azurecontainer.io:5000/get-user-settings'
    
    response_code, error, data = fetch_data_from_microservice(url, user_id)
    return response_code, error, data

@app.route("/home", methods=["GET"])
def home():
    user_id = request.args.get('user_id', default=2, type=int)

    response_code, settings_error, data = fetch_user_settings(user_id)

    # if error or not data:
    #     return render_template("home.html", error=error or "User not found")
    
    profile = data[0] if data else {}
    
    # Here you would filter blogs and comments based on the user_id
    # Assuming these functions return the appropriate data 
    blogs, blog_ids = filter_blogs_by_user(user_id, blog_data)
    comments = filter_comments_by_blog_ids(blog_ids, comment_data)

    return render_template("home.html", blogs=blogs, comments=comments, profile=profile, error=settings_error)

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404

@app.route("/profile", methods=["GET"])
def profile():
    user_id = request.args.get('user_id', default=None, type=int)
    
    # Placeholder for fetching user settings. Replace with actual data retrieval.
    profile = None if not user_id else {"user_id": user_id, "user_name": "JaneDoe", "cooking_level": "Intermediate", "birthday": "1990-01-01"}
    
    if not profile:
        # No profile found; pass an empty profile object to the template.
        return render_template("profile.html", profile={}, error="No profile found. Please input your details.")
    
    return render_template("profile.html", profile=profile)

# Assuming an update-profile route to handle POST requests
@app.route("/update-profile", methods=["POST"])
def update_profile():
    # Here, you'd retrieve form data and update the profile accordingly.
    # This function would eventually send data to a microservice to write to database.
    
    # For now, redirect back to the profile page as a placeholder.
    return redirect(url_for('profile'))

#for login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None  # Initialize error message to None
    if request.method == 'POST':
        user_id = request.form['user_id']
        password = request.form['password']
        # Hardcoded validation for demonstration purposes
        if user_id != "admin" or password != "password":
            error = 'Invalid credentials. Please try again.'
        else:
            # Assuming you have a route named 'home' for the home page
            return redirect(url_for('home'))  # Redirect to home on success
    return render_template('login.html', error=error)