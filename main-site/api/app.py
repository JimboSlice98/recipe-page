import os
import pyodbc
from datetime import timedelta
import requests
from dotenv import load_dotenv
from flask import (Flask, abort, redirect, render_template, request, session,
                   url_for, jsonify, session, flash)
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from azure.data.tables import TableServiceClient, TableClient

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
register_user_details = __import__(f"{base_path}.helper_login", fromlist=['register_user_details']).register_user_details
register_user_password = __import__(f"{base_path}.helper_login", fromlist=['register_user_password']).register_user_password

# Configure flask server
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Initialise Database manager
MessagesDatabaseManager.initialize_database()

# Intialise the Image Storage Manager
image_storage_manager = ImageStorageManager()


################## START MESSAGES PATHS ##################


function_base_url ="https://comments-function.azurewebsites.net"

@app.route('/messages', methods=['GET'])
@login_required
def get_messages():
    user_id = request.args.get('user_id', default=int(current_user.id), type=int)
    function_url = f"{function_base_url}/messages?user_id={user_id}"
    print(function_url)
    response = requests.get(function_url)
    if response.ok:
        return render_template('messages.html', user_id=user_id, conversations=response.json())
    else:
        print("\n/Messages Function failed!\n")
        conversations = MessagesDatabaseManager.get_user_id_conversations(user_id)
        return render_template("messages.html", user_id=user_id, conversations=conversations)


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


@app.route('/post_message', methods=['POST'])
@login_required
def post_message():
    message_data = request.json
    function_url = f"{function_base_url}/post_message"
    response = requests.post(function_url, json=message_data)

    if response.ok:
        print("posted the messsage")
        return jsonify(response.json()), 200
    else:
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
##################### START AI PATHS #####################


@app.route('/generate-recipe', methods=['POST'])
@login_required
def generate_recipe():
    try:
        user_input = request.form['prompt']
        output = get_recipe_from_prompt(user_input)
        print("here is the output that we pass to jinja\n\n", output)
        return jsonify(output)
    
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500


##################### END AI PATHS #####################
############### START IMAGE STORAGE PATH ###############


app.config['UPLOAD_FOLDER'] = 'static/images'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

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
####################### START FUNCTIONS ######################


def extract_recipe_ids(user_id, recipes):
    processed_recipes = {}
    recipe_ids = []
    for recipe in recipes:
        processed_recipes[recipe['blog_id']] = recipe
        recipe_ids.append(recipe['blog_id'])
    return processed_recipes, recipe_ids


def fetch_data_from_microservice(url, id_type=None, id_value=None):
    try:
        params = {id_type: str(id_value)} if id_value is not None else {}
        response = requests.get(url, params=params)
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
    

def fetch_user_details(user_id=None):
    url = 'http://sse-user-details.uksouth.azurecontainer.io:5000/get-user-details'
    
    response_code, error, data = fetch_data_from_microservice(url, "user_id", user_id)
    print("data from fetch function is", response_code, error, data)
    return response_code, error, data


def fetch_comments():
    url = 'http://sse-comments.uksouth.azurecontainer.io:5000/get-comments'
    
    response_code, error, data = fetch_data_from_microservice(url)
    print("data from fetch function is", response_code, error, data)
    return response_code, error, data


def fetch_recipes(user_id=None):
    url = 'http://sse-recipes.uksouth.azurecontainer.io:5000/get-recipe-details'
    
    response_code, error, data = fetch_data_from_microservice(url, "user_id", user_id)
    print("data from fetch function is", response_code, error, data)
    return response_code, error, data


######################## END FUNCTIONS #######################
################### START MAIN PAGE ROUTING ##################


@app.route("/", methods=["GET"])
def index():
    if current_user.is_authenticated:
        return redirect(url_for('home', user_id=current_user.get_id()))
    return render_template("index.html")


@app.route("/home", methods=["GET"])
@login_required
def home():
    user_id = request.args.get('user_id', default=int(current_user.id), type=int)
    response_code, settings_error, user_data = fetch_user_details(user_id)
    response_code, settings_error, recipe_data = fetch_recipes(user_id)
    response_code, settings_error, comments = fetch_comments()
    
    profile = user_data[0] if user_data else {}    
    recipes, recipe_ids = extract_recipe_ids(user_id, recipe_data)    
    images_by_blog = {}

    for recipe_id in recipe_ids:        
        images_metadata = image_storage_manager.fetch_images_metadata(user_id, recipe_id)
        images_by_blog[recipe_id] = image_storage_manager.generate_blob_urls_by_blog_id(images_metadata)

    if profile == {}:
        return render_template("no-user.html")
    else:    
        return render_template("home.html", user_id=user_id, blogs=recipes, comments=comments, profile=profile, images_by_blog=images_by_blog, error=settings_error)
    

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    abort(404)


@app.before_request
def redirect_https_to_http():
    if request.is_secure:
        http_url = request.url.replace('https://', 'http://', 1)
        return redirect(http_url, code=301)


@app.errorhandler(404)
def not_found(e):
    return render_template("no-recipe.html"), 404


@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '').lower().strip()
    users = fetch_user_details()[-1]

    if not query:
        return render_template('no_results.html', users=users)

    exact_match = None
    partial_matches = []

    for user in users:
        if query == user['display_name'].lower():
            exact_match = user
            break
        elif query in user['display_name'].lower():
            partial_matches.append(user)

    if exact_match:
        return redirect(url_for('home', user_id=exact_match['user_id']))
    elif partial_matches:
        if len(partial_matches) == 1:
            return redirect(url_for('home', user_id=partial_matches[0]['user_id']))
        else:
            return render_template('search_results.html', query=query, users=partial_matches)
    else:
        return render_template('no_results.html', query=query, users=users)


@app.route("/profile", methods=["GET"])
@login_required
def profile():
    user_id = current_user.id
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
    
    try:
        response = requests.post(microservice_url, json=payload)
        
        if response.status_code == 200:
            return redirect(url_for('home'))
        else:
            return redirect(url_for('profile', user_id=user_id, error='Failed to update profile'))
    except requests.exceptions.RequestException as e:
        print(str(e))
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
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    error = None
    if request.method == 'POST':
        display_name = request.form.get('display_name')
        password = request.form.get('password')
        passwordnot = request.form.get('passwordnot')

        if password != passwordnot:
            error = 'Passwords do not match!'
            return render_template('register.html', error=error)

        user_id = register_user_details(display_name)
        if user_id == None:
            error = 'Unable to register user, please try again later'
            return render_template('register.html', error=error)
        
        if register_user_password(user_id, password):            
            return render_template('register.html', user_id=user_id, error=error)

        error = 'Unable to register user, please try again later'
    
    return render_template('register.html', error=error)
