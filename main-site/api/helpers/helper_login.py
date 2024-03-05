import pyodbc
import os

def authenticate_user(user_id, password):
    try:
        # Establish connection to the database
        conn_str = (
            f"Driver={{{os.environ['AUTHENTICATION_DRIVER']}}};"
            f"Server={os.environ['AUTHENTICATION_SERVER']};"
            f"Database={os.environ['AUTHENTICATION_DATABASE']};"
            f"UID={os.environ['AUTHENTICATION_USERNAME']};"
            f"PWD={os.environ['AUTHENTICATION_PASSWORD']};"
        )
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Execute query to check user credentials
        query = "SELECT * FROM Userauth WHERE user_id = ? AND password = ?"
        cursor.execute(query, (user_id, password))
        user = cursor.fetchone()
        
        if user:
            return True  # User authenticated successfully
        else:
            return False  # Authentication failed
    except pyodbc.Error as e:
        # Handle database errors
        print(f"Database error: {e}")
        return False
    finally:
        # Close database connection
        cursor.close()
        conn.close()

# def get_database_connection():
#     try:
#         # Establish connection to the database
#         conn_str = (
#             f"Driver={{{os.environ['AUTHENTICATION_DRIVER']}}};"
#             f"Server={os.environ['AUTHENTICATION_SERVER']};"
#             f"Database={os.environ['AUTHENTICATION_DATABASE']};"
#             f"UID={os.environ['AUTHENTICATION_USERNAME']};"
#             f"PWD={os.environ['AUTHENTICATION_PASSWORD']};"
#         )
#         conn = pyodbc.connect(conn_str)
#         return conn
#     except pyodbc.Error as e:
#         # Handle database connection errors
#         print(f"Database connection error: {e}")
#         return None

# def close_database_connection(conn):
#     try:
#         if conn:
#             conn.close()
#     except pyodbc.Error as e:
#         # Handle database disconnection errors
#         print(f"Database disconnection error: {e}")

# def execute_query(query, params=None):
#     conn = None
#     try:
#         conn = get_database_connection()
#         if conn:
#             cursor = conn.cursor()
#             if params:
#                 cursor.execute(query, params)
#             else:
#                 cursor.execute(query)
#             return cursor
#     except pyodbc.Error as e:
#         # Handle query execution errors
#         print(f"Query execution error: {e}")
#         return None
#     finally:
#         close_database_connection(conn)

# def authenticate_user(user_id, password):
#     try:
#         # Execute query to check user credentials
#         query = "SELECT * FROM Userauth WHERE user_id = ? AND password = ?"
#         cursor = execute_query(query, (user_id, password))
#         if cursor:
#             user = cursor.fetchone()
#             return True if user else False
#         else:
#             return False
#     except Exception as e:
#         # Handle other exceptions
#         print(f"Exception: {e}")
#         return False
