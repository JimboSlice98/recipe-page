import os
from datetime import timedelta

import requests
from dotenv import load_dotenv
from flask import (Flask, abort, redirect, render_template, request, session,
                   url_for, jsonify)

# from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from azure.data.tables import TableServiceClient, TableClient


import pyodbc


load_dotenv()

# Database class to handle contacting Message
from api.helpers.helper_db_messages import MessagesDatabaseManager 

# Get function to contact openAI
from api.helpers.helper_AI import get_recipe_from_prompt

# Images database class to contact Messages
from api.helpers.helper_db_images import ImageStorageManager, comment_data, blog_data

# # # For development?
# from helpers.helper_db_messages import MessagesDatabaseManager 

# # Get function to contact openAI
# from helpers.helper_AI import get_recipe_from_prompt

# # Images database class to contact Messages
# from helpers.helper_db_images import ImageStorageManager, comment_data, blog_data

# Import helper functions for login
#from api.helpers.helper_login import authenticate_user
from helpers.helper_login import authenticate_user


# Configure app.py
app = Flask(__name__)


# Initialise Database manager
MessagesDatabaseManager.initialize_database()

# Intialise the Image Storaga Manager
image_storage_manager = ImageStorageManager()

################### START MESSAGES PATHS ###################

function_base_url ="https://comments-function.azurewebsites.net"


@app.route('/messages', methods=['GET'])
def get_messages():
    user_id = request.args.get('user_id')
    function_url = f"{function_base_url}/messages?user_id={user_id}"
    response = requests.get(function_url)
    if response.ok:
        return render_template('messages.html', conversations=response.json())
    else:
        return "Error fetching messages", response.status_code


@app.route('/start_chat', methods=['POST'])
def start_chat():
    message_data = request.json
    function_url = f"{function_base_url}/post_message"
    response = requests.post(function_url, json=message_data)
    if response.ok:
        return jsonify(response.json()), 200
    else:
        return "Error starting chat", response.status_code


@app.route('/post_message', methods=['POST'])
def post_message():
    # Extract the JSON payload from the incoming request
    message_data = request.json

    # Construct the URL to your Azure Function endpoint for posting a message
    function_url = f"{function_base_url}/post_message"

    # Make a POST request to the Azure Function endpoint with the message data
    response = requests.post(function_url, json=message_data)

    # Check if the request to the Azure Function was successful
    if response.ok:
        # Return the JSON response from the Azure Function
        return jsonify(response.json()), 200
    else:
        # In case of an error, return an error response
        return jsonify({'status': 'error', 'message': 'Failed to post message'}), response.status_code


@app.route('/get_messages/<int:user_id1>/<int:user_id2>', methods=['GET'])
def get_user_messages(user_id1, user_id2):
    function_url = f"{function_base_url}/get_messages?user_id1={user_id1}&user_id2={user_id2}"
    response = requests.get(function_url)
    if response.ok:
        messages_list = response.json()
        return jsonify(messages_list), 200
    else:
        return "Error fetching messages", response.status_code


# @app.route('/post_message', methods=['POST'])
# def post_message():
#     message_data = request.json
#     MessagesDatabaseManager.insert_message(message_data)
#     return jsonify({'status': 'success', 'status_code': 200}), 200


# @app.route('/get_messages/<int:user_id1>/<int:user_id2>', methods=['GET'])
# def get_user_messages(user_id1, user_id2):
#     messages = MessagesDatabaseManager.get_ordered_messages([user_id1, user_id2])
#     messages_list = [
#             {
#                 'chat_id': message[0],
#                 'user_id1': message[1],
#                 'user_id2': message[2],
#                 'message': message[3],
#                 'sender': message[4],
#                 # Convert datetime to a string format, e.g., ISO format
#                 'time_stamp': message[5].isoformat() if isinstance(message[5], datetime) else message[5]
#             }
#             for message in messages
#         ]
#     return jsonify(messages_list), 200


# @app.route('/start_chat', methods=['POST'])
# def start_chat():
#     message_data = request.json
#     # Inserts a blank message into the table for a new chat
#     MessagesDatabaseManager.insert_message(message_data) 
#     return jsonify({'status': 'success', 'message': 'Chat started'}), 200


# @app.route('/messages', methods=['GET'])
# def get_messages():   
    
#     user_id = request.args.get('user_id', 1, type=int)  # Default to 1 if not specified
#     conversations = MessagesDatabaseManager.get_user_id_conversations(user_id)
#     return render_template("messages.html", user_id=user_id, conversations=conversations)

################### END MESSAGES PATHS ###################

################### START AI PATHS ###################

@app.route('/generate-recipe', methods=['POST'])
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
def display_images():
    user_id = request.args.get('user_id')
    blog_id = request.args.get('blog_id')

    images_metadata = image_storage_manager.fetch_images_metadata(user_id, blog_id)
    blob_urls_by_blog_id = image_storage_manager.generate_blob_urls_by_blog_id(images_metadata)

    return render_template('display_images.html', blob_urls_by_blog_id=blob_urls_by_blog_id)

@app.route('/delete-image', methods=['POST'])
def delete_image():
    data = request.form
    blob_url = data.get('blob_url')
    blob_name = blob_url.split("/")[-1]
    unique_id, user_id = blob_name.split("_")[:2]
    user_id = user_id.split(".")[0]

    image_storage_manager.delete_image_from_blob(blob_name)
    image_storage_manager.delete_image_metadata(user_id, unique_id)

    return redirect(url_for('home', user_id=user_id)) 


# Is this used? Need to check
@app.route('/upload', methods=['GET'])
def upload_form():
    # Just render the upload form template, no need to generate a SAS token
    # The upload_form.html does the post request to below
    return render_template('upload_form.html')


@app.route('/upload-image', methods=['POST'])
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
        # Assume insert_image_metadata takes user_id, blog_id, original_filename, and a datetime string or object (`date`)
        image_storage_manager.insert_image_metadata(user_id, blog_id, original_filename, date)
        return redirect(url_for('home', user_id=user_id))  
    
    except:
        print("failed")
        # set to 100 so home will redirect to 404 page for now
        return redirect(url_for('home'), user_id=100)    

################### END IMAGE STORAGE PATH ###################


@app.route("/", methods=["GET"])
def index():
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
    
def fetch_user_settings(user_id):
    url = 'http://sse-user-details.uksouth.azurecontainer.io:5000/get-user-details'
    # url = 'http://127.0.0.1:5000/get-user-details'
    
    response_code, error, data = fetch_data_from_microservice(url, "user_id", user_id)
    print("data from fetch function is", response_code, error, data)
    return response_code, error, data

def fetch_comments(blog_id):
    url = 'http://sse-comments.uksouth.azurecontainer.io:5000/get-comments'
    
    response_code, error, data = fetch_data_from_microservice(url, "blog_id", blog_id)
    print("data from fetch function is", response_code, error, data)
    return response_code, error, data



@app.route("/home", methods=["GET"])
def home():
    user_id = request.args.get('user_id', default=2, type=int)

    # response_code, settings_error, data = fetch_user_details(user_id)
    
    # profile = data[0] if data else {}
    # blog_data = request_reiceps_details(user_id):

    blogs, blog_ids = filter_blogs_by_user(user_id, blog_data)
    comments = filter_comments_by_blog_ids(blog_ids, comment_data)


    
    # Will return a 
    response_code, settings_error, user_data = fetch_user_settings(user_id)
    
    profile = user_data[0] if user_data else {}
    
    # blogs, blog_ids = filter_blogs_by_user(user_id, blog_data)
    # comments = filter_comments_by_blog_ids(blog_ids, comment_data)


    # Fetch images metadata for each blog_id and generate URLs
    images_by_blog = {}
    for blog_id in blog_ids:
        # images_metadata = fetch_all_images_metadata(user_id, blog_id)
        images_metadata = image_storage_manager.fetch_images_metadata(user_id, blog_id)
        # images_by_blog[blog_id] = generate_blob_urls_by_blog_id(images_metadata)
        images_by_blog[blog_id] = image_storage_manager.generate_blob_urls_by_blog_id(images_metadata)
    
    if blogs:   
        return render_template("home.html", user_id = user_id, blogs=blogs, comments=comments, profile=profile, images_by_blog=images_by_blog, error=settings_error)
    else:
        return render_template("no-recipe.html")
    

@app.route("/404", methods=["GET"])
def not_found(e):
    return render_template("no-recipe.html"), 404


@app.route("/no-users", methods=["GET"])
def not_users():
    return render_template("no-recipe.html")


@app.route("/profile", methods=["GET"])
def profile():
    user_id = request.args.get('user_id', default=None, type=int)
    print("/proflile user_id", user_id)
    
    # Simulated response from a data fetching function
    response_code, settings_error, profile = fetch_user_settings(user_id)
    # response = (200, None, [{'cooking_level': 'Intermediate', 'display_name': 'John Doe', 'email': 'johndoe@example.com', 'favorite_cuisine': 'Mexican', 'location': 'Los Angeles, USA', 'personal_website': '', 'profile_picture_url': 'https://example.com/profiles/johndoe.jpg', 'short_bio': 'Starting my culinary journey with tacos.', 'user_id': 2}])
    print("profile data passed in", profile)
    profile = profile[0]
    
    if not profile:
        return render_template("profile.html", user_id=user_id, profile={}, error="No profile found. Please input your details.")
    
    return render_template("profile.html", user_id=user_id, profile=profile, error=settings_error)


@app.route("/update-profile", methods=["POST"])
def update_profile():
    # Extract the form data from the request
    form_data = request.form
    user_id = request.form.get('user_id')
    print("update profile user_id", user_id)

    # Construct the data payload to send to the microservice
    payload = {
        'UserID': user_id,  # Assuming you have a hidden input for the UserID in your form, form_data.get('user_id')
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
    
    # The URL of the microservice endpoint
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

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None  # Initialize error message to None
    if request.method == 'POST':
        user_id = request.form['user_id']
        password = request.form['password']
        
        if authenticate_user(user_id, password):
            # Redirect to home page with user_id
            return redirect(url_for('home', user_id=user_id))
        else:
            error = 'Invalid credentials. Please try again.'
    
    # Render login page with error message
    return render_template('login.html', error=error)


# Simple register page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        return 'Registration successful'
    return render_template('register.html')


@app.route("/get-authentication", methods=["GET"])
def get_authentication():
    user_id = request.args.get("user_id")

    print(
        f"Driver   = {{{os.environ['AUTHENTICATION_DRIVER']}}};\n"
        f"Server   = {os.environ['AUTHENTICATION_SERVER']};\n"
        f"Database = {os.environ['AUTHENTICATION_DATABASE']};\n"
        f"UID      = {os.environ['AUTHENTICATION_USERNAME']};\n"
        f"PWD      = {os.environ['AUTHENTICATION_PASSWORD']};\n"
        )

    try:
        conn_str = (
            f"Driver={{{os.environ['AUTHENTICATION_DRIVER']}}};"
            f"Server={os.environ['AUTHENTICATION_SERVER']};"
            f"Database={os.environ['AUTHENTICATION_DATABASE']};"
            f"UID={os.environ['AUTHENTICATION_USERNAME']};"
            f"PWD={os.environ['AUTHENTICATION_PASSWORD']};"
        )
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        data = {'message': 'Hello, world!'}
        return jsonify(data)

        cursor.execute(query, params)
        rows = cursor.fetchall()

    except pyodbc.Error as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500
    
# # # Example usage
# if __name__ == "__main__":
# #     # Dummy data for insertion
# #     # dummy_data = [
# #     #     {'user_id1': 1, 'user_id2': 2, 'message': 'Hey there!', 'sender': 1},
# #     #     {'user_id1': 2, 'user_id2': 1, 'message': 'Hello!', 'sender': 2},
# #     #     {'user_id1': 1, 'user_id2': 3, 'message': 'How are you doing?', 'sender': 1},
# #     #     {'user_id1': 2, 'user_id2': 3, 'message': 'Good morning!', 'sender': 2},
# #     #     {'user_id1': 3, 'user_id2': 1, 'message': 'Good night!', 'sender': 3}
# #     # ]

# #     # # Insert each message
# #     # for data in dummy_data:
# #     #     insert_message(data)

# #     user_ids = [1, 2]

# #     for message in get_ordered_messages(user_ids):
# #         print(message)
#     a = get_user_id_conversations(1)
#     print(a)

# Turn debug mode for testing
# if __name__ == '__main__':
#     app.run(debug=True)