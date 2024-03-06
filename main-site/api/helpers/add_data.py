import pyodbc
import os
import bcrypt
from dotenv import load_dotenv

load_dotenv()

# Salts and hashes a password
def salt_and_hash(password):
    bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(bytes, salt)
    return hash.decode('utf-8')

# Generate password hash
hashed_password = salt_and_hash('password5')

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

    # Insert new user into Users table
    query = "INSERT INTO Users (user_id, password_hash) VALUES (?, ?)"
    cursor.execute(query, (5, hashed_password))  # Replace 1 with the desired user_id
    conn.commit()
    print("New user added successfully.")
except pyodbc.Error as e:
    print(f"Database error: {e}")
finally:
    cursor.close()
    conn.close()
