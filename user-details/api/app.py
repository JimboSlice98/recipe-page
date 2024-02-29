import pyodbc
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import os, requests


load_dotenv()


app = Flask(__name__)

# Helper function to connect to the database
def get_db_connection():
    conn_str = (
        f"Driver={{{os.environ['USER_DETAILS_DRIVER']}}};"
        f"Server={os.environ['USER_DETAILS_SERVER']};"
        f"Database={os.environ['USER_DETAILS_DATABASE']};"
        f"UID={os.environ['USER_DETAILS_USERNAME']};"
        f"PWD={os.environ['USER_DETAILS_PASSWORD']};"
    )
    return pyodbc.connect(conn_str)

# Helper function to execute a read (SELECT) query
def execute_read_query(query, params=()):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

# Helper function to execute a write (INSERT, UPDATE) query
def execute_write_query(query, params):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor.rowcount

@app.route("/get-user-details", methods=["GET"])
def get_user_details():
    user_id = request.args.get("user_id")
    if user_id:
        query = "SELECT * FROM user_details_complete WHERE UserID = ?"
        params = (user_id,)
    else:
        query = "SELECT * FROM user_details_complete"
        params = ()
    
    rows = execute_read_query(query, params)

    users_details = [
        {
            "user_id": row.UserID,
            "email": row.Email,
            "display_name": row.DisplayName,
            "cooking_level": row.CookingLevel,
            "favorite_cuisine": row.FavoriteCuisine,
            "short_bio": row.ShortBio,
            "profile_picture_url": row.ProfilePictureUrl,
            "personal_website": row.PersonalWebsite,
            "location": row.Location
        } for row in rows
    ]

    return jsonify(users_details) if users_details else jsonify({"error": "No data found"}), 404

@app.route("/update-user-details", methods=["POST"])
def update_user_details():
    data = request.json
    user_id = data.get("UserID")
    if not user_id or not str(user_id).isdigit():
        return jsonify({"error": "UserID is required and must be a valid integer"}), 400

    fields_to_update = {field: data[field] for field in ['Email', 'DisplayName', 'CookingLevel', 'FavoriteCuisine', 'ShortBio', 'ProfilePictureUrl', 'PersonalWebsite', 'Location'] if field in data}
    update_parts = [f"{field} = ?" for field in fields_to_update]
    update_statement = f"UPDATE user_details_complete SET {', '.join(update_parts)} WHERE UserID = ?"
    update_params = list(fields_to_update.values()) + [user_id]

    rowcount = execute_write_query(update_statement, update_params)

    if rowcount == 0:
        return jsonify({"error": "No user found with the provided UserID or no changes made"}), 404
    else:
        return jsonify({"success": "User details updated successfully"}), 200

# Keep the root route and Flask app initialization as they were
@app.route("/", methods=["GET"])
def root():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
