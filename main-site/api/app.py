import json
import os
import secrets
from datetime import timedelta
import pyodbc
#from flask_sqlalchemy import SQLAlchemy
#from app import app, db  # Assuming 'app' is your Flask application instance and 'db' is your SQLAlchemy instance
#from models import User

import requests
from dotenv import load_dotenv
from flask import (Flask, abort, redirect, render_template, request, session,
                   url_for, jsonify)
# from flask_login import (LoginManager, current_user, login_required,                          login_user, logout_user)
# from oauthlib.oauth2 import WebApplicationClient
from requests.exceptions import HTTPError, RequestException

# from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from azure.data.tables import TableServiceClient, TableClient

load_dotenv()
from openai import OpenAI
import openai

client = OpenAI()

# Configure app.py
app = Flask(__name__)

# Load your OpenAI API key from an environment variable for security
try:
    openai.api_key = os.getenv("OPENAI_API_KEY")
except:
    openai.api_key = None

def get_recipe_from_prompt(user_input):
    # Only use this when we need it, as charging per request
    if "admin" in user_input:
        try:
            if len(user_input) > 100:
                return 
            prompt = f"{user_input} - give me a recipe for the before. i want you do give the answers in dictionary format with  title: x, ingredients: y, steps: x .x string and y and z should be a list of strings, so then i will use the dictionary values based on the keys)"
            print(prompt)

        # Use the client to create a chat completion
            chat_completion = client.chat.completions.create(
                messages=[{
                    "role": "user",
                    "content": prompt,
                }],
                model="gpt-3.5-turbo",
            )

            # response = chat_completion.choices[0].message['content']
            response = chat_completion.choices[0].message.content

            # use this line if we are in production!
            # Convert JSON string to Python dictionary
            response_dict = json.loads(response)
        except:
            response_dict = {
        "title": "error to ai",
        "ingredients": ["error", "er"], 
        "steps": ["err", "err"]
            }
        
        return response_dict
    else:
        
        response = {
        "title": "Chocolate Cake",
        "ingredients": [
            "1 and 3/4 cups all-purpose flour",
            "2 cups granulated sugar",
            "3/4 cup unsweetened cocoa powder",
            "2 teaspoons baking soda",
            "1 teaspoon baking powder",
            "1 teaspoon salt",
            "2 large eggs",
            "1 cup buttermilk",
            "1/2 cup vegetable oil",
            "2 teaspoons vanilla extract",
            "1 cup hot water"
        ],
        "steps": [
            "Preheat oven to 350°F (175°C) and grease and flour two 9-inch round cake pans.",
            "In a large bowl, whisk together flour, sugar, cocoa powder, baking soda, baking powder, and salt.",
            "Add eggs, buttermilk, oil, and vanilla extract to the dry ingredients and mix until well combined.",
            "Stir in hot water until the batter is smooth and pour into prepared cake pans.",
            "Bake for 30-35 minutes or until a toothpick inserted into the center comes out clean.",
            "Let the cakes cool in the pans for 10 minutes, then transfer to a wire rack to cool completely.",
            "Frost and decorate as desired. Enjoy your delicious chocolate cake!"
        ]
        }
        # note this doesnt work when live!!!!
        return dict(response)
    

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
    

### IMAGE STORAGE STUFF ###
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


def fetch_images_metadata(user_id, blog_id):
    images_metadata = {blog_id: []} 
    try:
        # Connect to the table
        table_client = TableClient.from_connection_string(conn_str=IMAGE_STORAGE_CONNECTION_STRING, table_name=IMAGE_STORAGE_TABLE_NAME)
        # Initialize with the specific blog_id
        # images_metadata = []
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
                # print("gen blob url: addded to the key: ", blog_id, "and the value: ", blob_url)
                blob_urls_by_blog_id[blog_id].append(blob_url)
                # print(f"Blob URL for blog {blog_id}: {blob_url}")
        # print("here is the url we passed in!!!", blob_urls_by_blog_id)
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
    
    try:
        table_client = TableClient.from_connection_string(conn_str=storage_connection_string, table_name="ImageMetadata")
        entity = table_client.get_entity(partition_key=str(user_id), row_key=unique_id)
        return entity
    except Exception as e:
        print(f"Entity could not be found: {e}")
        return None


def delete_image_metadata(user_id, unique_id):
    try:
        # Create a table client
        table_client = TableServiceClient.from_connection_string(IMAGE_STORAGE_CONNECTION_STRING).get_table_client(table_name=IMAGE_STORAGE_TABLE_NAME)
        # Delete the entity
        table_client.delete_entity(partition_key=str(user_id), row_key=str(unique_id))
        print(f"Metadata for {unique_id} deleted successfully.")
    except Exception as e:
        print(f"Failed to delete metadata: {e}")


def upload_image_to_blob(container_name, blob_name, upload_file_path):
    """
    Uploads a local file to Azure Blob Storage.
    """
    try:
        blob_service_client = BlobServiceClient.from_connection_string(IMAGE_STORAGE_CONNECTION_STRING)
        
        # Create the container if it doesn't exist
        container_client = blob_service_client.get_container_client(container_name)
        try:
            container_client.create_container()
        except Exception as e:
            print(f"Container already exists or another error occurred: {e}")
    except:
        print("couldnt connect to the image storage")

    # Create a blob client using the local file name as the name for the blob
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

    # Upload the local file to blob storage
    with open(upload_file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)
    
    print(f"File {upload_file_path} uploaded to {container_name}/{blob_name}")


def delete_image_from_blob(container_name, blob_name):
    try:
        # Create a blob client
        blob_client = BlobServiceClient.from_connection_string(IMAGE_STORAGE_CONNECTION_STRING).get_blob_client(container=container_name, blob=blob_name)
        # Delete the blob
        blob_client.delete_blob()
        print(f"Blob {blob_name} deleted successfully.")
    except Exception as e:
        print(f"Failed to delete blob: {e}")


def get_blob_sas_url(container_name, blob_name):
    """
    Generates a SAS URL for accessing a blob.
    """
    try:
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
    except:
        return "failed"

app.config['UPLOAD_FOLDER'] = 'static/images'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB upload limit


@app.route('/display-images')
def display_images():
    user_id = request.args.get('user_id')
    blog_id = request.args.get('blog_id')

    images_metadata = fetch_images_metadata(user_id, blog_id)
    # images_metadata = fetch_all_images_metadata(user_id)
    blob_urls_by_blog_id = generate_blob_urls_by_blog_id(images_metadata)

    # Render a template to display images organized by blog_id
    return render_template('display_images.html', blob_urls_by_blog_id=blob_urls_by_blog_id)

@app.route('/delete-image', methods=['POST'])
def delete_image():
    data = request.form
    blob_url = data.get('blob_url')
    print("trying to delete the blob", blob_url)
    
    # Extract the blob name from the blob_url
    # https://sserecipestorage.blob.core.windows.net/sse-recipe-storage-container/20240223021611_2.jpgblog_id1233
    blob_name = blob_url.split("/")[-1]
    
    # sse-recipe-storage-container/20240223021611_2.jpgblog_id1233

    # Decode the unique filename to get user_id and unique_id
    unique_id, user_id = blob_name.split("_")[:2]
    print(f"unique id {unique_id} and user_id {user_id}")
    # get only the number before the .jpg etc
    user_id = user_id.split(".")[0]
    
    # Remove the image from blob storage
    delete_image_from_blob(IMAGE_STORAGE_CONTAINER_NAME, blob_name)
    
    # Remove the metadata from the table
    delete_image_metadata(user_id, unique_id)
    
    return redirect(url_for('home', user_id=user_id))


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
        if not user_id:
            user_id = 1
        if not blog_id:
            blog_id = 1
        
        unique_filename, date = generate_unique_filename(original_filename, user_id, blog_id)

        #### WILL NEED TO REMOVE #####
        # print(f"unique_filename: {unique_filename}")  # For debugging purposes
        try:
            # Get a blob client and upload the file stream directly to Azure Blob Storage
            blob_service_client = BlobServiceClient.from_connection_string(IMAGE_STORAGE_CONNECTION_STRING)
            blob_client = blob_service_client.get_blob_client(container=IMAGE_STORAGE_CONTAINER_NAME, blob=unique_filename)
            
            # Upload the file stream to Azure Blob Storage
            blob_client.upload_blob(file, blob_type="BlockBlob", overwrite=True)

            # Insert metadata into Azure Table Storage
            insert_image_metadata(IMAGE_STORAGE_CONNECTION_STRING, user_id, blog_id, original_filename, date)

            return redirect(url_for('home', user_id=user_id))
        except:
            print("failed")
            return redirect(url_for('404'))
        # return redirect(url_for('show_uploaded_image', filename=unique_filename))


# Will need to remove
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
    try:
        table_client = TableClient.from_connection_string(conn_str=storage_connection_string, table_name=IMAGE_STORAGE_TABLE_NAME)
    except:
        print("failed to connect: insert_image_metadata")
        return redirect(url_for('404'))

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
    
    # print("\n\n\n in home", images_by_blog, "\n\n\n")
    if blogs:   
        return render_template("home.html", blogs=blogs, comments=comments, profile=profile, images_by_blog=images_by_blog, error=settings_error)
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

#
#@app.route("/get-user-authentication", methods=["GET"])
@app.route("/test", methods=["GET"])
#def get_user_authentication():
def test():
    user_id = request.args.get("user_id")

    print(
        f"Driver   = {{{os.environ['USER_AUTHENTICATION_DRIVER']}}};\n"
        f"Server   = {os.environ['USER_AUTHENTICATION_SERVER']};\n"
        f"Database = {os.environ['USER_AUTHENTICATION_DATABASE']};\n"
        f"UID      = {os.environ['USER_AUTHENTICATION_USERNAME']};\n"
        f"PWD      = {os.environ['USER_AUTHENTICATION_PASSWORD']};\n"
        )

    try:
        conn_str = (
            f"Driver={{{os.environ['USER_AUTHENTICATION_DRIVER']}}};"
            f"Server={os.environ['USER_AUTHENTICATION_SERVER']};"
            f"Database={os.environ['USER_AUTHENTICATION_DATABASE']};"
            f"UID={os.environ['USER_AUTHENTICATION_USERNAME']};"
            f"PWD={os.environ['USER_AUTHENTICATION_PASSWORD']};"
        )
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        #stack overflow troubleshooting
        #https://stackoverflow.com/questions/50046158/pyodbc-login-timeout-error
        #https://stackoverflow.com/questions/56053724/microsoftodbc-driver-17-for-sql-serverlogin-timeout-expired-0-sqldriverco
        #connection = pyodbc.connect("DRIVER={ODBC Driver 17 for SQL Server};SERVER=myserver;DATABASE=mydb;UID=myuser;PWD=mypassword", autocommit=True)

        
        
        # if user_id:
        #     query = "SELECT * FROM "User""
        #     params = (user_id,)
        # else:
        #     query = "SELECT * FROM "User""
        #     params = ()

        if user_id:
            query = 'SELECT * FROM "User"'
            params = (user_id,)
        else:
            query = 'SELECT * FROM "User"'
            params = ()

        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # users_details = [{"user_id": row.user_id, "cooking_level": row.cooking_level, "birthday": row.birthday.strftime("%Y-%m-%d")} for row in rows]
        
        # if users_details:
        #     return jsonify(users_details)
        # else:
        #     return jsonify({"error": "No data found"}), 404

    except pyodbc.Error as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

# # SQLAlchemy configuration
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://sse-user-authentication-admin:fTH4&qrse$$Geq@sse-user-authentication-server.database.windows.net/sse-user_authentication-database?driver=ODBC+Driver+17+for+SQL+Server'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)

# # Define your database model
# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     first_name = db.Column(db.String(100))
#     last_name = db.Column(db.String(100))
#     gender = db.Column(db.String(20))
#     date_of_birth = db.Column(db.Date)
#     email = db.Column(db.String(120), unique=True)
#     postcode = db.Column(db.String(20))
#     password = db.Column(db.String(100))

#     def __repr__(self):
#         return f'<User {self.id}>'

# # Flask route
# @app.route("/test", methods=["GET"])
# def get_user_authentication():
#     user_id = request.args.get("user_id")

#     try:
#         if user_id:
#             user = User.query.get(user_id)
#             if user:
#                 user_data = {
#                     "user_id": user.id,
#                     "first_name": user.first_name,
#                     "last_name": user.last_name,
#                     "gender": user.gender,
#                     "date_of_birth": user.date_of_birth.strftime("%Y-%m-%d"),
#                     "email": user.email,
#                     "postcode": user.postcode,
#                     "password": user.password
#                 }
#                 return jsonify(user_data)
#             else:
#                 return jsonify({"error": "User not found"}), 404
#         else:
#             users = User.query.all()
#             users_data = [{
#                 "user_id": user.id,
#                 "first_name": user.first_name,
#                 "last_name": user.last_name,
#                 "gender": user.gender,
#                 "date_of_birth": user.date_of_birth.strftime("%Y-%m-%d"),
#                 "email": user.email,
#                 "postcode": user.postcode,
#                 "password": user.password
#             } for user in users]
#             return jsonify(users_data)

#     except Exception as e:
#         return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

# if __name__ == '__main__':
#     app.run(debug=True)