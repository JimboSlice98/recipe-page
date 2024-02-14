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


@app.route("/get-user-settings", methods=["GET"])
def get_user_settings():
    user_id = request.args.get("user_id")

    try:
        conn_str = (
            f"Driver={{{os.environ['SETTING_DB_DRIVER']}}};"
            f"Server={os.environ['SETTING_DB_SERVER']};"
            f"Database={os.environ['SETTING_DB_NAME']};"
            f"UID={os.environ['SETTING_DB_USER']};"
            f"PWD={os.environ['SETTING_DB_PASS']};"
        )
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        if user_id:
            query = "SELECT * FROM user_settings WHERE user_id = ?"
            params = (user_id,)
        else:
            query = "SELECT * FROM user_settings"
            params = ()

        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        users_settings = [{"user_id": row.user_id, "cooking_level": row.cooking_level, "birthday": row.birthday.strftime("%Y-%m-%d")} for row in rows]
        
        if users_settings:
            return jsonify(users_settings)
        else:
            return jsonify({"error": "No data found"}), 404

    except pyodbc.Error as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500


@app.route("/home", methods=["GET"])
def home():
    user_id = 2  # The user ID you want to fetch settings for
    # url = 'http://20.108.67.30:5000/get-user-settings'
    url = 'http://dnsawdrsseusersettings.uksouth.azurecontainer.io:5000/get-user-settings'
    
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


@app.route("/", methods=["GET"])
def root():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

