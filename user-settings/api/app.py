import pyodbc
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import os, requests

load_dotenv()  # This loads the .env file into the environment

app = Flask(__name__)

# Hardcoded data for demonstration purposes
users_settings = {
    "1": {"user_id": "1", "cooking_level": "Expert Chef", "birthday": "1990-01-01"},
    "2": {"user_id": "2", "cooking_level": "Novice", "birthday": "1992-02-02"},
    # Add more user settings as needed
}

# def get_user_settings_data(user_id):
#     try:
#         conn_str = (
#             f"Driver={{{os.environ['SETTING_DB_DRIVER']}}};"
#             f"Server={os.environ['SETTING_DB_SERVER']};"
#             f"Database={os.environ['SETTING_DB_NAME']};"
#             f"UID={os.environ['SETTING_DB_USER']};"
#             f"PWD={os.environ['SETTING_DB_PASS']};"
#         )

#         # Connect to your Azure SQL database
#         conn = pyodbc.connect(conn_str)
#         cursor = conn.cursor()
        
#         # Query the database
#         cursor.execute("SELECT * FROM user_settings WHERE user_id = ?", user_id)
#         row = cursor.fetchone()
#         # ...
#         if row:
#             return {
#                 "success": True,
#                 "data": {
#                     "user_id": row.user_id,
#                     "cooking_level": row.cooking_level,
#                     "birthday": row.birthday.strftime("%Y-%m-%d")
#                 }
#             }
#         else:
#             return {
#                 "success": False,
#                 "error": "User not found"
#             }
#     except pyodbc.Error as e:
#         return {
#             "success": False,
#             "error": "Database connection or execution problem",
#             "details": str(e)
#         }
#     # Handle other exceptions similarly

# @app.route("/get-user-settings", methods=["POST"])
# def get_user_settings():
#     data = request.json
#     user_id = data.get("user_id")
#     result = get_user_settings_data(user_id)
    
#     if result["success"]:
#         return jsonify(result["data"])
#     else:
#         return jsonify({"error": result["error"]}), 500 if "details" in result else 404

# @app.route("/home", methods=["GET"])
# def home():
#     user_id = 1  # The user ID you want to test with
    
#     result = get_user_settings_data(user_id)
    
#     if result["success"]:
#         return render_template("index.html", profile=result["data"])
#     else:
#         return render_template("index.html", error=result["error"])


@app.route("/get-user-settings", methods=["POST"])
def get_user_settings():
    data = request.json
    user_id = data.get("user_id")
    

    try:
        print("trying to connect")
        # Connection string using environment variables
        conn_str = (
            f"Driver={{{os.environ['SETTING_DB_DRIVER']}}};"
            f"Server={os.environ['SETTING_DB_SERVER']};"
            f"Database={os.environ['SETTING_DB_NAME']};"
            f"UID={os.environ['SETTING_DB_USER']};"
            f"PWD={os.environ['SETTING_DB_PASS']};"
        )

        # Connect to your Azure SQL database
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Query the database
        cursor.execute("SELECT * FROM user_settings WHERE user_id = ?", user_id)
        row = cursor.fetchone()
        print("post select")
        print(row)
        
        # If a user setting is found, return it as JSON
        if row:
            return jsonify({
                "user_id": row.user_id,
                "cooking_level": row.cooking_level,
                "birthday": row.birthday.strftime("%Y-%m-%d")
            })
        else:
            # If no data is found for the user, return a default or error message
            return jsonify({"error": "User not found", "user_id": "NOT_FOUND", "cooking_level": "NOT_FOUND", "birthday": "NOT_FOUND"}), 404

    except pyodbc.Error as e:
        error_message = str(e)
        print(f"Database error: {error_message}")

        # Inspect the error message for specific keywords to categorize the error
        if "login failed" in error_message.lower():
            return jsonify({"error": "Authentication failed", "details": error_message}), 500
        elif "could not open a connection" in error_message.lower():
            return jsonify({"error": "Could not connect to database", "details": error_message}), 500
        elif "table or view does not exist" in error_message.lower():
            return jsonify({"error": "Database schema error", "details": error_message}), 500
        else:
            return jsonify({"error": "Database operation error", "details": error_message}), 500

    except Exception as e:
        # Handle other exceptions
        print(f"Unexpected error: {e}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

    # data = request.json
    # user_id = data.get("user_id")
    # user_settings = users_settings.get(user_id)

    # if user_settings:
    #     return jsonify(user_settings)
    # else:
    #     return jsonify({"error": "User not found"}), 404

@app.route("/home", methods=["GET"])
def home():
    user_id = 2  # The user ID you want to test with
    # response = requests.post('http://localhost:5000/get-user-settings', json={"user_id": str(user_id)})
    response = requests.post('http://dnsawdrsseusersettings.uksouth.azurecontainer.io:5000/get-user-settings', json={"user_id": str(user_id)})
    # response = get_user_settings()
    print("fin database read")
    data = response.json()
    
    if response.status_code == 200:
        return render_template("index.html", profile=data)
    else:
        return render_template("index.html", error=data['error'])


@app.route("/", methods=["GET"])
def root():
    # temporary
    return render_template("index.html")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

