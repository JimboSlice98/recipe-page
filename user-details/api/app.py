import pyodbc
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import os, requests


load_dotenv()


app = Flask(__name__)


@app.route("/get-user-details", methods=["GET"])
def get_user_details():
    user_id = request.args.get("user_id")    

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
            query = "SELECT * FROM user_details_complete WHERE UserID = ?"
            params = (user_id,)
        else:
            query = "SELECT * FROM user_details_complete"
            params = ()

        cursor.execute(query, params)
        # cursor.execute(query)
        rows = cursor.fetchall()

        for row in rows:
            print(row)
        
        # users_details = [{"user_id": row.user_id, "cooking_level": row.cooking_level, "birthday": row.birthday.strftime("%Y-%m-%d")} for row in rows]
        users_details = [
            {
                "user_id": row.UserID,  # Make sure this matches the case used in the database
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
    user_id = request.args.get("UserID")  # Ensure the case matches the database schema
    if not user_id:
        return jsonify({"error": "UserID is required"}), 400

    # Dictionary to hold the fields to update
    fields_to_update = {}

    # Check for each field in the request's query parameters
    for field in ['Email', 'DisplayName', 'CookingLevel', 'FavoriteCuisine', 'ShortBio', 'ProfilePictureUrl', 'PersonalWebsite', 'Location']:
        if request.args.get(field):
            fields_to_update[field] = request.args.get(field)
    
    # If no fields are provided to update, return an error
    if not fields_to_update:
        return jsonify({"error": "No fields provided for update"}), 400
    
    # Construct the UPDATE statement dynamically based on the fields provided
    update_parts = [f"{field} = ?" for field in fields_to_update.keys()]
    update_statement = f"UPDATE user_details_complete SET {', '.join(update_parts)} WHERE UserID = ?"

    # Parameters for the UPDATE statement
    update_params = list(fields_to_update.values()) + [user_id]

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

        # Execute the UPDATE statement
        cursor.execute(update_statement, update_params)
        conn.commit()  # Commit the changes to the database

        if cursor.rowcount == 0:
            return jsonify({"error": "No user found with the provided UserID or no changes made"}), 404
        else:
            return jsonify({"success": "User details updated successfully"}), 200

    except pyodbc.Error as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route("/", methods=["GET"])
def root():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
