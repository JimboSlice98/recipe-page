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
        f"Driver   = {{{os.environ['SETTING_DB_DRIVER']}}};\n"
        f"Server   = {os.environ['SETTING_DB_SERVER']};\n"
        f"Database = {os.environ['SETTING_DB_NAME']};\n"
        f"UID      = {os.environ['SETTING_DB_USER']};\n"
        f"PWD      = {os.environ['SETTING_DB_PASS']};\n"
        )

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
            query = "SELECT * FROM user_details WHERE user_id = ?"
            params = (user_id,)
        else:
            query = "SELECT * FROM user_details"
            params = ()

        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        users_details = [{"user_id": row.user_id, "cooking_level": row.cooking_level, "birthday": row.birthday.strftime("%Y-%m-%d")} for row in rows]
        
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

