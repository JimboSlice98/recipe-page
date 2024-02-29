import pyodbc
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

@app.route("/get-recipe-details", methods=["GET"])
def get_recipe_details():
    user_id = request.args.get("user_id")

    print(
        f"Driver   = {{{os.environ['RECIPES_DRIVER']}}};\n"
        f"Server   = {os.environ['RECIPES_SERVER']};\n"
        f"Database = {os.environ['RECIPES_DATABASE']};\n"
        f"UID      = {os.environ['RECIPES_USERNAME']};\n"
        f"PWD      = {os.environ['RECIPES_PASSWORD']};\n"
    )

    try:
        conn_str = (
            f"Driver={{{os.environ['RECIPES_DRIVER']}}};"
            f"Server={os.environ['RECIPES_SERVER']};"
            f"Database={os.environ['RECIPES_DATABASE']};"
            f"UID={os.environ['RECIPES_USERNAME']};"
            f"PWD={os.environ['RECIPES_PASSWORD']};"
        )
        try:
            conn = pyodbc.connect(conn_str)
            # Log a successful connection
            app.logger.info("Successfully connected to the database.")
        except pyodbc.Error as e:
            app.logger.error(f"Database connection failed: {e}")

        cursor = conn.cursor()

        if user_id:
            # Fetch recipes for a specific user
            query = "SELECT blog_id, user_id, blog_title, blog_description, likes FROM recipes WHERE user_id = ?"
            params = (user_id,)
        else:
            # Fetch all recipes
            query = "SELECT blog_id, user_id, blog_title, blog_description, likes FROM recipes"
            params = ()

        cursor.execute(query, params)
        rows = cursor.fetchall()

        recipes_data = [
            {
                'blog_id': row.blog_id,
                'user_id': row.user_id,
                'blog_title': row.blog_title,
                'blog_description': row.blog_description,
                'likes': row.likes
            } for row in rows
        ]

        if recipes_data:
            return jsonify(recipes_data)
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
