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

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from azure.data.tables import TableServiceClient, TableClient

# Configure app.py
app = Flask(__name__)

# image storage connection constants
try:
    IMAGE_STORAGE_CONNECTION_STRING = os.environ.get('IMAGE_STORAGE_CONNECTION_STRING')
    IMAGE_STORAGE_CONTAINER_NAME = os.environ.get('IMAGE_STORAGE_CONTAINER_NAME')
    IMAGE_STORAGE_ACCOUNT_NAME = os.environ.get('IMAGE_STORAGE_ACCOUNT_NAME')
    IMAGE_STORAGE_TABLE_NAME = os.environ.get('IMAGE_STORAGE_TABLE_NAME')
except:
    print("\n\n\ndidnt get image_storage varaibles\n\n\n")

# Initialize the Table Service Client
try:
    table_service_client = TableServiceClient.from_connection_string(conn_str=IMAGE_STORAGE_CONNECTION_STRING)
    table_client = table_service_client.get_table_client(table_name=IMAGE_STORAGE_TABLE_NAME)
except Exception as e:
    print(f"An unexpected error occurred: {e}")

# def fetch_all_images_metadata(user_id):
#     # Connect to the table
#     table_client = TableClient.from_connection_string(conn_str=IMAGE_STORAGE_CONNECTION_STRING, table_name=IMAGE_STORAGE_TABLE_NAME)
#     images_metadata = {}

#     try:
#         # Query to filter by user_id (PartitionKey)
#         query_filter = f"PartitionKey eq '{user_id}'"
#         entities = table_client.query_entities(query_filter)

#         for entity in entities:
#             blog_id = entity['BlogId']
#             if blog_id not in images_metadata:
#                 images_metadata[blog_id] = []
#             images_metadata[blog_id].append(entity)
#         return images_metadata
#     except Exception as e:
#         print(f"Error fetching entities: {e}")
#         return None
    
# def fetch_images_metadata(user_id, blog_id):
#     # Connect to the table
#     table_client = TableClient.from_connection_string(conn_str=IMAGE_STORAGE_CONNECTION_STRING, table_name=IMAGE_STORAGE_TABLE_NAME)
#     images_metadata = []

#     try:
#         # Query to filter by user_id (ParitionKey) and blog_id (BlogId)
#         query_filter = f"PartitionKey eq '{user_id}' and BlogId eq '{blog_id}'"
#         entities = table_client.query_entities(query_filter)

#         for entity in entities:
#             images_metadata.append(entity)
#         return images_metadata
#     except Exception as e:
#         print(f"Error fetching entities: {e}")
#         return None


# def fetch_all_images_metadata(user_id):
#     # Connect to the table
#     table_client = TableClient.from_connection_string(conn_str=IMAGE_STORAGE_CONNECTION_STRING, table_name=IMAGE_STORAGE_TABLE_NAME)
#     images_metadata = {}

#     try:
#         # Query to filter by user_id (PartitionKey)
#         query_filter = f"PartitionKey eq '{user_id}'"
#         entities = table_client.query_entities(query_filter)

#         for entity in entities:
#             blog_id = entity['BlogId']
#             if blog_id not in images_metadata:
#                 images_metadata[blog_id] = []
#             images_metadata[blog_id].append(entity)
#         return images_metadata
#     except Exception as e:
#         print(f"Error fetching entities: {e}")
#         return None

# def fetch_images_metadata(user_id, blog_id):
#     print(user_id, blog_id)
#     # blog_id = 1
#     # Connect to the table
#     table_client = TableClient.from_connection_string(conn_str=IMAGE_STORAGE_CONNECTION_STRING, table_name=IMAGE_STORAGE_TABLE_NAME)
#     # images_metadata = {blog_id: [] for blog_id in blog_id}  # Initialize dictionary with empty lists for each blog_id
#     images_metadata = {}

#     try:
#         # Iterate over each blog_id and fetch entities for each
#         # for blog_id in blog_ids:
#         query_filter = f"PartitionKey eq '{user_id}' and BlogId eq '{blog_id}'"
#         entities = table_client.query_entities(query_filter)
#         for entity in entities:
#             # Add the entity to the corresponding blog_id key
#             images_metadata[blog_id].append(entity)
#     except Exception as e:
#         print(f"Error fetching entities: {e}")
#         # Handle error, possibly return None or keep the empty lists
#     print(images_metadata)
#     return images_metadata

def fetch_images_metadata(user_id, blog_id):
    # Connect to the table
    table_client = TableClient.from_connection_string(conn_str=IMAGE_STORAGE_CONNECTION_STRING, table_name=IMAGE_STORAGE_TABLE_NAME)
    images_metadata = {blog_id: []} # Initialize with the specific blog_id
    # images_metadata = []

    try:
        # Create the query filter for a single blog_id
        query_filter = f"PartitionKey eq '{user_id}' and BlogId eq '{blog_id}'\n"
        entities = table_client.query_entities(query_filter)

        for entity in entities:
            # Add the entity to the list for the specified blog_id
            images_metadata[blog_id].append(entity)
            # images_metadata.append(entity)

    except Exception as e:
        print(f"Error fetching entities: {e}")

    return images_metadata



# def fetch_images_metadata(user_id, blog_id):
#     # Connect to the table
#     table_client = TableClient.from_connection_string(conn_str=IMAGE_STORAGE_CONNECTION_STRING, table_name=IMAGE_STORAGE_TABLE_NAME)
#     images_metadata = []

#     try:
#         # Query to filter by user_id (ParitionKey) and blog_id (BlogId)
#         query_filter = f"PartitionKey eq '{user_id}' and BlogId eq '{blog_id}'"
#         entities = table_client.query_entities(query_filter)

#         for entity in entities:
#             images_metadata.append(entity)
#         return images_metadata
#     except Exception as e:
#         print(f"Error fetching entities: {e}")
#         return None


# def generate_blob_urls_from_metadata(images_metadata):
#     blob_urls = []

#     for metadata in images_metadata:
#         # Reconstruct the unique filename using the stored metadata
#         extension = metadata['Extension']
#         unique_id = metadata['RowKey']
#         user_id = metadata['PartitionKey']
#         blog_id = metadata['BlogId']
#         # original_filename = metadata['OriginalFilename']

#         # RowKey is datetime - unique part
#         # date_userid-extension-blog_id       
#         filename = f"{unique_id}_{user_id if user_id else 'guest'}{extension}{blog_id}"

#         # Construct the full blob URL
#         blob_url = f"https://{IMAGE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{IMAGE_STORAGE_CONTAINER_NAME}/{filename}"
#         blob_urls.append(blob_url)
#         print(f"Blob URL: {blob_url}")  # For debugging purposes

#     return blob_urls
   
def generate_blob_urls_by_blog_id(images_metadata):
    blob_urls_by_blog_id = {}

    try:
        for blog_id, metadata_list in images_metadata.items():
            blob_urls_by_blog_id[blog_id] = []

            for metadata in metadata_list:
                extension = metadata['Extension']
                unique_id = metadata['RowKey']
                user_id = metadata['PartitionKey']

                # Construct the blob name and URL
                filename = f"{unique_id}_{user_id}{extension}{blog_id}"
                blob_url = f"https://{IMAGE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{IMAGE_STORAGE_CONTAINER_NAME}/{filename}"
                # added blob_url[blog_id] instead of blob_url for now 
                print("gen blob url: addded to the key: ", blog_id, "and the value: ", blob_url)
                blob_urls_by_blog_id[blog_id].append(blob_url)
                print(f"Blob URL for blog {blog_id}: {blob_url}")
        print("here is the url we passed in!!!", blob_urls_by_blog_id)
    except:
        if metadata:
            print("metadata was okay")
        else:
            print("meta data was bad")
            
    return blob_urls_by_blog_id

def generate_unique_filename(original_filename, user_id=1, blog_id=1):
    extension = os.path.splitext(original_filename)[1]
    unique_id = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{unique_id}_{user_id if user_id else 'guest'}{extension}{blog_id}"
    return filename

# Function to retrieve entities for a user_id and a list of blog_ids
def get_image_metadata(storage_connection_string, user_id, unique_id):
    table_client = TableClient.from_connection_string(conn_str=storage_connection_string, table_name="ImageMetadata")

    try:
        entity = table_client.get_entity(partition_key=str(user_id), row_key=unique_id)
        return entity
    except Exception as e:
        print(f"Entity could not be found: {e}")
        return None


def upload_image_to_blob(container_name, blob_name, upload_file_path):
    """
    Uploads a local file to Azure Blob Storage.
    """
    blob_service_client = BlobServiceClient.from_connection_string(IMAGE_STORAGE_CONNECTION_STRING)
    
    # Create the container if it doesn't exist
    container_client = blob_service_client.get_container_client(container_name)
    try:
        container_client.create_container()
    except Exception as e:
        print(f"Container already exists or another error occurred: {e}")

    # Create a blob client using the local file name as the name for the blob
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

    # Upload the local file to blob storage
    with open(upload_file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)
    
    print(f"File {upload_file_path} uploaded to {container_name}/{blob_name}")

def get_blob_sas_url(container_name, blob_name):
    """
    Generates a SAS URL for accessing a blob.
    """
    blob_service_client = BlobServiceClient.from_connection_string(IMAGE_STORAGE_CONNECTION_STRING)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

    sas_token = generate_blob_sas(account_name=IMAGE_STORAGE_ACCOUNT_NAME,
                                  container_name=container_name,
                                  blob_name=blob_name,
                                  account_key=blob_service_client.credential.account_key,
                                  permission=BlobSasPermissions(read=True),
                                  expiry=datetime.utcnow() + timedelta(hours=1))  # Token valid for 1 hour

    blob_url_with_sas = f"https://{IMAGE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{container_name}/{blob_name}?{sas_token}"
    return blob_url_with_sas

app.config['UPLOAD_FOLDER'] = 'static/images'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB upload limit

# @app.route('/display-images')
# def display_images():
#     user_id = request.args.get('user_id')
#     # blog_id = request.args.get('blog_id')  # Assuming a single blog_id is used for this request

#     images_metadata = fetch_images_metadata(user_id, blog_id)
#     blob_urls = generate_blob_urls_from_metadata(images_metadata)

#     # Render a template to display images
#     return render_template('display_images.html', blob_urls=blob_urls)

@app.route('/display-images')
def display_images():
    user_id = request.args.get('user_id')
    blog_id = request.args.get('blog_id')

    images_metadata = fetch_images_metadata(user_id, blog_id)
    # images_metadata = fetch_all_images_metadata(user_id)
    blob_urls_by_blog_id = generate_blob_urls_by_blog_id(images_metadata)

    # Render a template to display images organized by blog_id
    return render_template('display_images.html', blob_urls_by_blog_id=blob_urls_by_blog_id)


@app.route('/upload', methods=['GET'])
def upload_form():
    # Just render the upload form template, no need to generate a SAS token
    # The upload_form.html does the post request to below
    return render_template('upload_form.html')

@app.route('/upload-image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return redirect(request.url)
    file = request.files['image']
    if file.filename == '':
        return "No selected file", 400
        # return redirect(request.url)
    if file:
        original_filename = file.filename
        
        # Retrieve user_id and blog_id from form data
        user_id = request.form.get('user_id')
        blog_id = request.form.get('blog_id')
        unique_filename, date = generate_unique_filename(original_filename, user_id, blog_id)

        #### WILL NEED TO REMOVE #####
        print(f"unique_filename: {unique_filename}")  # For debugging purposes
        
        # Get a blob client and upload the file stream directly to Azure Blob Storage
        blob_service_client = BlobServiceClient.from_connection_string(IMAGE_STORAGE_CONNECTION_STRING)
        blob_client = blob_service_client.get_blob_client(container=IMAGE_STORAGE_CONTAINER_NAME, blob=unique_filename)
        
        # Upload the file stream to Azure Blob Storage
        blob_client.upload_blob(file, blob_type="BlockBlob", overwrite=True)

        # Insert metadata into Azure Table Storage
        insert_image_metadata(IMAGE_STORAGE_CONNECTION_STRING, user_id, blog_id, original_filename, date)

        return redirect(url_for('home'))
        # return redirect(url_for('show_uploaded_image', filename=unique_filename))

@app.route('/show-uploaded-image/<filename>')
def show_uploaded_image(filename):
    image_url = get_blob_sas_url(IMAGE_STORAGE_CONTAINER_NAME, filename)
    return render_template("show_image.html", image_url=image_url)

def generate_unique_filename(original_filename, user_id=1, blog_id=1):
    extension = os.path.splitext(original_filename)[1]
    unique_id = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{unique_id}_{user_id if user_id else 'guest'}{extension}{blog_id}"
    return filename, unique_id

   
def insert_image_metadata(storage_connection_string, user_id, blog_id, original_filename, date):
    # Generate unique parts of the filename
    unique_id = date
    extension = os.path.splitext(original_filename)[1]
    # unique_id = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{unique_id}_{user_id if user_id else 'guest'}{blog_id}{extension}"

    # Create a table client
    table_client = TableClient.from_connection_string(conn_str=storage_connection_string, table_name=IMAGE_STORAGE_TABLE_NAME)

    # Define the entity to insert
    entity = {
        "PartitionKey": str(user_id),
        "RowKey": unique_id,
        "BlogId": str(blog_id),
        "OriginalFilename": original_filename,
        "Extension": extension,
        "Timestamp": datetime.now()
    }

    # Insert the entity
    table_client.create_entity(entity=entity)

    return filename

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
    url = 'http://sse-user-details.uksouth.azurecontainer.io:5000/get-user-details'
    
    response_code, error, data = fetch_data_from_microservice(url, user_id)
    return response_code, error, data

# @app.route("/home", methods=["GET"])
# def home():
#     user_id = request.args.get('user_id', default=2, type=int)

#     response_code, settings_error, data = fetch_user_settings(user_id)

#     # if error or not data:
#     #     return render_template("home.html", error=error or "User not found")
    
#     profile = data[0] if data else {}
    
#     # Here you would filter blogs and comments based on the user_id
#     # Assuming these functions return the appropriate data 
#     blogs, blog_ids = filter_blogs_by_user(user_id, blog_data)
#     comments = filter_comments_by_blog_ids(blog_ids, comment_data)

#     return render_template("home.html", blogs=blogs, comments=comments, profile=profile, error=settings_error)

@app.route("/home", methods=["GET"])
def home():
    user_id = request.args.get('user_id', default=2, type=int)

    response_code, settings_error, data = fetch_user_settings(user_id)
    
    profile = data[0] if data else {}
    
    blogs, blog_ids = filter_blogs_by_user(user_id, blog_data)
    comments = filter_comments_by_blog_ids(blog_ids, comment_data)

    # Fetch images metadata for each blog_id and generate URLs
    images_by_blog = {}
    for blog_id in blog_ids:
        # images_metadata = fetch_all_images_metadata(user_id, blog_id)
        images_metadata = fetch_images_metadata(user_id, blog_id)
        # images_by_blog[blog_id] = generate_blob_urls_by_blog_id(images_metadata)
        images_by_blog[blog_id] = generate_blob_urls_by_blog_id(images_metadata)
    
    print("\n\n\n in home", images_by_blog, "\n\n\n")

    return render_template("home.html", blogs=blogs, comments=comments, profile=profile, images_by_blog=images_by_blog, error=settings_error)



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


#nma just added for register page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Here you can handle the form data after validation.
        # For this example, we'll just return a simple message.
        # In a real application, you should handle the data properly.
        return 'Registration successful'
    return render_template('register.html')