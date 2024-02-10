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

@app.route("/get-user-settings", methods=["POST"])
def get_user_settings():
    data = request.json
    user_id = data.get("user_id")

    try:
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
        # Handle database connection errors or query execution errors
        print(f"Database error: {e}")
        return jsonify({"error": "Database connection or execution problem", "details": str(e)}), 500

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
    user_id = 1  # The user ID you want to test with
    # response = requests.post('http://localhost:5000/get-user-settings', json={"user_id": str(user_id)})
    response = requests.post('http://dnsawdrsseusersettings.uksouth.azurecontainer.io:5000/get-user-settings', json={"user_id": str(user_id)})
    
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

