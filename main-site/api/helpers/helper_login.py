import requests
import bcrypt
import pyodbc
import os
from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username


    @classmethod
    def authenticate(cls, user_id, password):
        authenticated = authenticate_user(user_id, password)
        if authenticated:
            username = get_username_from_id(user_id)
            return cls(id=user_id, username=username) if username else None
        else:
            return None

    @staticmethod
    def get(user_id):
        username = get_username_from_id(user_id)
        return User(id=user_id, username=username) if username else None


def authenticate_user(user_id, password):
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
        
        query = "SELECT password_hash FROM Users WHERE user_id = ?"
        cursor.execute(query, (user_id,))
        user = cursor.fetchone()
        
        if user:
            stored_hashed_password = user.password_hash
            if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password.encode('utf-8')):
                return True
            else:
                return False
        else:
            print("User not found")
            return False
    except pyodbc.Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def get_username_from_id(user_id):
    url = f"http://sse-user-details.uksouth.azurecontainer.io:5000/get-user-details"
    params = {'user_id': user_id}

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            user_details = response.json()
            if user_details:
                user_info = user_details[0]
                return user_info.get('display_name')
            else:
                return None
        else:
            print(f"Failed to fetch user details. Status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None


def salt_and_hash(password):
    bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(bytes, salt)
    return hash.decode('utf-8')