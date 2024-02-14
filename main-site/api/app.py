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
        'user_id': 'user235',
        'recipe_ingredients': '200g chocolate, 100g butter, 3 eggs, 150g sugar, 100g flour',
        'recipe_steps': '1. Melt chocolate and butter, 2. Mix in eggs and sugar, 3. Fold in flour, 4. Bake for 30 minutes'
    },
    'blog_id1236': {
        'blog_name': 'Healthy Kale Smoothie',
        'user_id': '2',
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


@app.route("/home", methods=["GET"])
def home():
    # get the current user_id from a session
    user_id = 2
    blogs, blog_ids = filter_blogs_by_user(user_id, blog_data)
    comments = filter_comments_by_blog_ids(blog_ids, comment_data)
    ""
    profile = {"user_id" : "user233", "cooking_level" : "amazing", "birthday": "every year" }
    
    user_id = 2  # The user ID you want to fetch settings for
    # url = 'http://20.108.67.30:5000/get-user-settings'
    url = 'http://dnsawdrsseusersettings.uksouth.azurecontainer.io:5000/get-user-settings'
    
    try:
        response = requests.get(url, params={"user_id": str(user_id)})
        if response.status_code == 200:
            data = response.json()
                    
            if data:
                profile = data[0]
                return render_template("home.html", blogs=blogs, comments=comments, profile=profile)
                # return render_template("index.html", profile=profile)
            else:            
                return render_template("home.html", error="User not found")
        else:
            return render_template("home.html", error=f"Failed to fetch user settings. Status code: {response.status_code}")
    
    except requests.exceptions.RequestException as e:
        return render_template("home.html", error=str(e))
    except ValueError as e:
        return render_template("home.html", error="Failed to decode JSON from response")


    # return index 1


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


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