import os
from datetime import timedelta

import requests
from dotenv import load_dotenv
from flask import (Flask, abort, redirect, render_template, request, session,
                   url_for, jsonify, session)
from flask_login import LoginManager, current_user, login_user, logout_user, login_required

# from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from azure.data.tables import TableServiceClient, TableClient

import pyodbc

load_dotenv()

# Determine the base import path depending on the environment
if os.environ.get("IS_PRODUCTION") == "PRODUCTION":
    base_path = "helpers"
else:
    base_path = "api.helpers"

# Dynamic import using the base path
MessagesDatabaseManager = __import__(f"{base_path}.helper_db_messages", fromlist=['MessagesDatabaseManager']).MessagesDatabaseManager
get_recipe_from_prompt = __import__(f"{base_path}.helper_AI", fromlist=['get_recipe_from_prompt']).get_recipe_from_prompt
ImageStorageManager = __import__(f"{base_path}.helper_db_images", fromlist=['ImageStorageManager']).ImageStorageManager
User = __import__(f"{base_path}.helper_login", fromlist=['User']).User
salt_and_hash = __import__(f"{base_path}.helper_login", fromlist=['salt_and_hash']).salt_and_hash

# Configure app.py
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Initialise Database manager
MessagesDatabaseManager.initialize_database()

# Intialise the Image Storaga Manager
image_storage_manager = ImageStorageManager()

################### START MESSAGES PATHS ###################

function_base_url ="https://comments-function.azurewebsites.net"

@app.route('/messages', methods=['GET'])
@login_required
def get_messages():
    user_id = request.args.get('user_id', default=1)
    function_url = f"{function_base_url}/messages?user_id={user_id}"
    print(function_url)
    response = requests.get(function_url)
    if response.ok:
        return render_template('messages.html', user_id=user_id, conversations=response.json())
    else:
        print("\n/Messages Function failed!\n")
        conversations = MessagesDatabaseManager.get_user_id_conversations(user_id)
        return render_template("messages.html", user_id=user_id, conversations=conversations)
        # return render_template('messages.html', conversations=response.json())


@app.route('/start_chat', methods=['POST'])
@login_required
def start_chat():
    message_data = request.json
    function_url = f"{function_base_url}/post_message"
    response = requests.post(function_url, json=message_data)
    if response.ok:
        return jsonify(response.json()), 200
    else:
        print("Start chat failed using messages function")
        MessagesDatabaseManager.insert_message(message_data) 
        return jsonify({'status': 'success', 'message': 'Chat started'}), 200
        # return "Error starting chat", response.status_code  


@app.route('/post_message', methods=['POST'])
@login_required
def post_message():
    # Extract the JSON payload from the incoming request
    message_data = request.json

    # Construct the URL to your Azure Function endpoint for posting a message
    function_url = f"{function_base_url}/post_message"

    # Make a POST request to the Azure Function endpoint with the message data
    response = requests.post(function_url, json=message_data)

    # Check if the request to the Azure Function was successful
    if response.ok:
        print("posted the messsage")
        # Return the JSON response from the Azure Function
        return jsonify(response.json()), 200
    else:
        # In case of an error, return an error response
        print("failed to post the message using function")
        MessagesDatabaseManager.insert_message(message_data)
        return jsonify({'status': 'success', 'status_code': 200}), 200
    

@app.route('/get_messages/<int:user_id1>/<int:user_id2>', methods=['GET'])
@login_required
def get_user_messages(user_id1, user_id2):
    function_url = f"{function_base_url}/get_messages?user_id1={user_id1}&user_id2={user_id2}"
    response = requests.get(function_url)
    if response.ok:
        messages_list = response.json()
        return jsonify(messages_list), 200
    else:
        print("get messages between users on function failed")
        messages = MessagesDatabaseManager.get_ordered_messages([user_id1, user_id2])
        messages_list = [
                {
                    'chat_id': message[0],
                    'user_id1': message[1],
                    'user_id2': message[2],
                    'message': message[3],
                    'sender': message[4],
                    # Convert datetime to a string format, e.g., ISO format
                    'time_stamp': message[5].isoformat() if isinstance(message[5], datetime) else message[5]
                }
                for message in messages
            ]
        return jsonify(messages_list), 200


################### END MESSAGES PATHS ###################

################### START AI PATHS ###################

@app.route('/generate-recipe', methods=['POST'])
@login_required
def generate_recipe():
    try:
        # use this line in production, but not in testing 
        user_input = request.form['prompt']
        # user_input = "a delicious chocolate cake"
        output = get_recipe_from_prompt(user_input)
        print("here is the output that we pass to jinja\n\n", output)
        # {title, ingredients, steps} - the keys
        return jsonify(output)
    
    except Exception as e:
        # Handle errors
        print(e)  # Print the error to the console
        return jsonify({'error': str(e)}), 500

################### END AI PATHS ###################

################### START IMAGE STORAGE PATH ###################

app.config['UPLOAD_FOLDER'] = 'static/images'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB upload limit

@app.route('/display-images')
@login_required
def display_images():
    user_id = request.args.get('user_id')
    blog_id = request.args.get('blog_id')

    images_metadata = image_storage_manager.fetch_images_metadata(user_id, blog_id)
    blob_urls_by_blog_id = image_storage_manager.generate_blob_urls_by_blog_id(images_metadata)
    print("\n\n/display-images worked", blob_urls_by_blog_id, "\n\n")

    return render_template('display_images.html', blob_urls_by_blog_id=blob_urls_by_blog_id)

@app.route('/delete-image', methods=['POST'])
@login_required
def delete_image():
    data = request.form
    blob_url = data.get('blob_url')
    blob_name = blob_url.split("/")[-1]
    unique_id, user_id = blob_name.split("_")[:2]
    user_id = user_id.split(".")[0]

    image_storage_manager.delete_image_from_blob(blob_name)
    image_storage_manager.delete_image_metadata(user_id, unique_id)

    return redirect(url_for('home', user_id=user_id)) 


@app.route('/upload-image', methods=['POST'])
@login_required
def upload_image():
    if 'image' not in request.files:
        return "No selected file", 400
    file = request.files['image']
    if file.filename == '':
        return redirect(request.url)
    original_filename = file.filename
    user_id = request.form.get('user_id', 1)
    blog_id = request.form.get('blog_id', 1)

    unique_filename, date = ImageStorageManager.generate_unique_filename(original_filename, user_id, blog_id)
    
    print("/upload image", unique_filename, date)
    try: 
        image_storage_manager.upload_image_to_blob(unique_filename, file)
        # Insert_image_metadata takes user_id, blog_id, original_filename, and a datetime string
        image_storage_manager.insert_image_metadata(user_id, blog_id, original_filename, date)
        return redirect(url_for('home', user_id=user_id))  
    
    except:
        print("failed")
        # set to 100 so home will redirect to 404 page for now
        return redirect(url_for('home'), user_id=100)    

################### END IMAGE STORAGE PATH ###################


@app.route("/", methods=["GET"])
def index():
    if current_user.is_authenticated:
        return redirect(url_for('home', user_id=current_user.get_id()))

    user_id = 2  # The user ID you want to fetch settings for
    url = 'http://sse-user-details.uksouth.azurecontainer.io:5000/get-user-details'
    
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

################### START FUNCTION CLUSTERFUCK ###################

def filter_blogs_by_user(user_id, blog_data):
    # user_id = str(user_id)
    filtered_blogs = {}
    blog_ids = []
    for blog in blog_data:
        if blog['user_id'] == user_id:
            filtered_blogs[blog['blog_id']] = blog
            blog_ids.append(blog['blog_id'])
    return filtered_blogs, blog_ids


def filter_comments_by_blog_ids(blog_ids, comment_data):
    filtered_comments = {}
    for blog_id in blog_ids:
        if blog_id in comment_data:
            filtered_comments[blog_id] = comment_data[blog_id]
    return filtered_comments

def fetch_data_from_microservice(url, id_type, id_value):
    try:
        response = requests.get(url, params={id_type: str(id_value)})
        # response = requests.get(url, params={user_id: str(user_id)})
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
    
def fetch_user_details(user_id):
    url = 'http://sse-user-details.uksouth.azurecontainer.io:5000/get-user-details'
    
    response_code, error, data = fetch_data_from_microservice(url, "user_id", user_id)
    print("data from fetch function is", response_code, error, data)
    return response_code, error, data

def fetch_comments():
    url = 'http://sse-comments.uksouth.azurecontainer.io:5000/get-comments'
    
    response_code, error, data = fetch_data_from_microservice(url, "", None)
    print("data from fetch function is", response_code, error, data)
    return response_code, error, data

def fetch_recipes(user_id):
    url = 'http://sse-recipes.uksouth.azurecontainer.io:5000/get-recipe-details'
    
    response_code, error, data = fetch_data_from_microservice(url, "user_id", user_id)
    print("data from fetch function is", response_code, error, data)
    return response_code, error, data

################### END FUNCTION CLUSTERFUCK ###################

@app.route("/home", methods=["GET"])
@login_required
def home():
    user_id = request.args.get('user_id', default=int(current_user.id), type=int)
    response_code, settings_error, user_data = fetch_user_details(user_id)
    response_code, settings_error, recipe_data = fetch_recipes(user_id)
    response_code, settings_error, comments = fetch_comments()
    
    profile = user_data[0] if user_data else {}
    
    blogs, blog_ids = filter_blogs_by_user(user_id, recipe_data)    

    images_by_blog = {}
    for blog_id in blog_ids:
        # images_metadata = fetch_all_images_metadata(user_id, blog_id)
        images_metadata = image_storage_manager.fetch_images_metadata(user_id, blog_id)
        # images_by_blog[blog_id] = generate_blob_urls_by_blog_id(images_metadata)
        images_by_blog[blog_id] = image_storage_manager.generate_blob_urls_by_blog_id(images_metadata)
    
    print("Images: ", images_by_blog)

    if profile == {}:
        return render_template("no-user.html")
    else:    
        return render_template("home.html", user_id = user_id, blogs=blogs, comments=comments, profile=profile, images_by_blog=images_by_blog, error=settings_error)
    
    

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    abort(404)


@app.errorhandler(404)
def not_found(e):
    return render_template("no-recipe.html"), 404


# @app.route("/no-users", methods=["GET"])
# def not_users():
#     return render_template("no-recipe.html")


@app.route("/profile", methods=["GET"])
@login_required
def profile():
    user_id = request.args.get('user_id', default=int(current_user.id), type=int)    
    response_code, settings_error, profile = fetch_user_details(user_id)
    profile = profile[0]    
    if not profile:
        return render_template("profile.html", user_id=user_id, profile={}, error="No profile found. Please input your details.")
    
    return render_template("profile.html", user_id=user_id, profile=profile, error=settings_error)


@app.route("/update-profile", methods=["POST"])
@login_required
def update_profile():
    form_data = request.form
    user_id = request.form.get('user_id')
    print("update profile user_id", user_id)

    payload = {
        'UserID': user_id,
        'Email': form_data.get('email'),
        'DisplayName': form_data.get('display_name'),
        'CookingLevel': form_data.get('cooking_level'),
        'FavoriteCuisine': form_data.get('favorite_cuisine'),
        'ShortBio': form_data.get('short_bio'),
        'ProfilePictureUrl': form_data.get('profile_picture_url'),
        'PersonalWebsite': form_data.get('personal_website'),
        'Location': form_data.get('location'),
    }
    print("in udpate profule the payload", payload)
    
    microservice_url = 'http://sse-user-details.uksouth.azurecontainer.io:5000/update-user-details'
    
    # this is for testing in live environment
    # microservice_url = 'http://sse-user-details.uksouth.azurecontainer.io:6000/update-user-details'
    # microservice_url = 'http://127.0.0.1:5000/update-user-details'
    
    try:
        # Send the POST request to the microservice
        response = requests.post(microservice_url, json=payload)
        
        # Check if the microservice successfully processed the request
        if response.status_code == 200:
            # Redirect to the profile page with a success message
            return redirect(url_for('profile', user_id=user_id, message='Profile updated successfully'))
        else:
            # Redirect to the profile page with an error message
            return redirect(url_for('profile', user_id=user_id, error='Failed to update profile'))
    except requests.exceptions.RequestException as e:
        # Handle any exceptions that occur during the request to the microservice
        print(e)
        return redirect(url_for('profile', user_id=user_id, error='An error occurred while updating the profile'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    error = None
    if request.method == 'POST':
        user_id = request.form['user_id']
        password = request.form['password']
        user = User.authenticate(user_id, password)

        if user:
            login_user(user)
            return redirect(url_for('home'))
        else:
            error = 'Invalid credentials. Please try again.'

    return render_template('login.html', error=error)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect("/")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        return 'Registration successful'
    return render_template('register.html')
