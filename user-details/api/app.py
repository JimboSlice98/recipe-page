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
            query = "SELECT * FROM user_details_complete WHERE user_id = ?"
            params = (user_id,)
        else:
            query = "SELECT * FROM user_details_complete"
            params = ()

        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # users_details = [{"user_id": row.user_id, "cooking_level": row.cooking_level, "birthday": row.birthday.strftime("%Y-%m-%d")} for row in rows]
        users_details = [
            {
                "user_id": row.user_id,
                "email": row.email,
                "display_name": row.display_name,
                "cooking_level": row.cooking_level,
                "favorite_cuisine": row.favorite_cuisine,
                "short_bio": row.short_bio,
                "profile_picture_url": row.profile_picture_url,
                "personal_website": row.personal_website,
                "location": row.location
            } for row in rows
        ]

        if users_details:
            return jsonify(users_details)
        else:
            return jsonify({"error": "No data found"}), 404

    except pyodbc.Error as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500


@app.route("/", methods=["GET"])
def root():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
