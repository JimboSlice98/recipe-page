import pyodbc
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
import os, requests


load_dotenv()


app = Flask(__name__)
CORS(app)


@app.route("/get-user-details", methods=["GET"])
def get_user_details():
    print("request to get user details")
    user_id = request.args.get("user_id")    
    print(user_id)

    print(
        f"Driver   = {{{os.environ['USER_DETAILS_DRIVER']}}};\n"
        f"Server   = {os.environ['USER_DETAILS_SERVER']};\n"
        f"Database = {os.environ['USER_DETAILS_DATABASE']};\n"
        f"UID      = {os.environ['USER_DETAILS_USERNAME']};\n"
        f"PWD      = {os.environ['USER_DETAILS_PASSWORD']};\n"
        )


    try:
        conn_str = (
            f"Driver={{{os.environ['USER_DETAILS_DRIVER']}}};"
            f"Server={os.environ['USER_DETAILS_SERVER']};"
            f"Database={os.environ['USER_DETAILS_DATABASE']};"
            f"UID={os.environ['USER_DETAILS_USERNAME']};"
            f"PWD={os.environ['USER_DETAILS_PASSWORD']};"
        )
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        if user_id:
            # query = "SELECT * FROM user_details WHERE user_id = ?"
            query = "SELECT * FROM user_details WHERE UserID = ?"
            params = (user_id,)
        else:
            query = "SELECT * FROM user_details"
            params = ()

        cursor.execute(query, params)
        # cursor.execute(query)
        rows = cursor.fetchall()
        
        # users_details = [{"user_id": row.user_id, "cooking_level": row.cooking_level, "birthday": row.birthday.strftime("%Y-%m-%d")} for row in rows]
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

        if users_details:
            print(users_details)
            return jsonify(users_details)
        else:
            return jsonify({"error": "No data found"}), 404

    except pyodbc.Error as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500


@app.route("/update-user-details", methods=["POST"])
def update_user_details():
    print("received a request to update_user_details in user-details")
    data = request.json
    print("here is the data", data)

    user_id = data.get("UserID")
    if not user_id:
        return jsonify({"error": "UserID is required"}), 400

    # Convert UserID to int if it's not None and is a digit
    try:
        user_id = int(user_id) if user_id and str(user_id).isdigit() else None
    except ValueError:
        return jsonify({"error": "UserID must be a valid integer"}), 400

    fields_to_update = {field: data[field] for field in ['Email', 'DisplayName', 'CookingLevel', 'FavoriteCuisine', 'ShortBio', 'ProfilePictureUrl', 'PersonalWebsite', 'Location'] if field in data}

    if not fields_to_update:
        return jsonify({"error": "No fields provided for update"}), 400

    update_parts = [f"{field} = ?" for field in fields_to_update]
    update_statement = f"UPDATE user_details SET {', '.join(update_parts)} WHERE UserID = ?"
    print(update_statement)

    update_params = list(fields_to_update.values()) + [user_id]
    print(update_params)

    try:
        conn_str = f"Driver={{{os.environ['USER_DETAILS_DRIVER']}}};Server={os.environ['USER_DETAILS_SERVER']};Database={os.environ['USER_DETAILS_DATABASE']};UID={os.environ['USER_DETAILS_USERNAME']};PWD={os.environ['USER_DETAILS_PASSWORD']};"
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        print("Connected to the database successfully.")

        cursor.execute(update_statement, update_params)
        conn.commit()

        print(f"Executed the update statement: {update_statement}")
        print(f"With parameters: {update_params}")
        print(f"Rows affected: {cursor.rowcount}")

        if cursor.rowcount == 0:
            return jsonify({"error": "No user found with the provided UserID or no changes made"}), 404
        else:
            return jsonify({"success": "User details updated successfully"}), 200
    except pyodbc.Error as e:
        print(f"Database error: {str(e)}")
        return jsonify({"error": "Database error", "details": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route("/add-user", methods=["POST"])
def add_user():
    print("Received a request to add a new user")
    data = request.json
    display_name = data.get("DisplayName")
    
    if not display_name:
        return jsonify({"error": "DisplayName is required"}), 400

    try:
        conn_str = (
            f"Driver={{{os.environ['USER_DETAILS_DRIVER']}}};"
            f"Server={os.environ['USER_DETAILS_SERVER']};"
            f"Database={os.environ['USER_DETAILS_DATABASE']};"
            f"UID={os.environ['USER_DETAILS_USERNAME']};"
            f"PWD={os.environ['USER_DETAILS_PASSWORD']};"
        )
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        query = "INSERT INTO user_details (DisplayName) VALUES (?)"
        cursor.execute(query, (display_name,))
        conn.commit()
        
        # Retrieve the new UserID generated by the auto-increment field
        new_user_id = cursor.execute("SELECT @@IDENTITY;").fetchval()
        print(f"Added new user with UserID: {new_user_id}")
        
        return jsonify({"success": "New user added successfully", "user_id": new_user_id}), 201

    except pyodbc.Error as e:
        print(f"Database error: {str(e)}")
        return jsonify({"error": "Database error", "details": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))