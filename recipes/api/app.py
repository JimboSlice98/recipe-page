from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from datetime import datetime
import uuid

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"postgresql://{os.getenv('RECIPES_USERNAME')}:"
    f"{os.getenv('RECIPES_PASSWORD')}@"
    f"{os.getenv('RECIPES_SERVER')}:"
    f"{os.getenv('RECIPES_PORT')}/"
    f"{os.getenv('RECIPES_DATABASE')}"
)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Recipe(db.Model):
    __tablename__ = 'blogs'

    blog_id = db.Column(db.String(50), primary_key=True)
    user_id = db.Column(db.Integer)
    blog_title = db.Column(db.String(255))
    blog_ingredients = db.Column(db.Text)
    blog_description = db.Column(db.Text)
    likes = db.Column(db.Integer)
    timestamp = db.Column(db.TIMESTAMP)


@app.route("/get-recipe-details", methods=["GET"])
def get_recipe_details():
    user_id = request.args.get("user_id", type=int)
    
    try:
        if user_id:
            recipes = Recipe.query.filter_by(user_id=user_id).all()
        else:
            recipes = Recipe.query.all()

        recipes_data = [
            {
                'blog_id': recipe.blog_id,
                'user_id': recipe.user_id,
                'blog_title': recipe.blog_title,
                'blog_ingredients': recipe.blog_ingredients,
                'blog_description': recipe.blog_description,
                'likes': recipe.likes,
                'timestamp': recipe.timestamp
            } for recipe in recipes
        ]
    
        if recipes_data:
            return jsonify(recipes_data)
        else:
            return jsonify({"error": "No data found"}), 404
    
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500


@app.route("/insert-recipe-details", methods=["POST"])
def insert_recipe_details():
    data = request.get_json()
    user_id = data.get('user_id')
    blog_id = f"{user_id}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"

    try:
        new_recipe = Recipe(
            blog_id=blog_id,
            user_id=user_id,
            blog_title=data.get('title'),
            blog_ingredients=data.get('ingredients'),
            blog_description=data.get('steps'),
            likes=data.get('likes', 0),
            timestamp=datetime.now()
        )

        db.session.add(new_recipe)
        db.session.commit()
        return jsonify({"message": "Recipe inserted successfully.", "blog_id": blog_id}), 201

    except Exception as e:
        db.session.rollback()
        print(str(e))
        return jsonify({"error": "An error occurred while inserting the recipe.", "details": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
    