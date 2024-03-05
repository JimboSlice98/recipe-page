from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from datetime import datetime
import uuid

load_dotenv()

app = Flask(__name__)
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
    blog_title = request.form.get('blog_title')
    blog_ingredients = request.form.get('blog_ingredients')
    blog_description = request.form.get('blog_description')
    user_id = request.form.get('user_id')
    blog_id = f"{user_id}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"

    # Parse data from the request
    data = request.get_json()
    
    try:
        # Create a new Recipe object
        new_recipe = Recipe(
            blog_id=data.get('blog_id'),
            user_id=data.get('user_id'),
            blog_title=data.get('blog_title'),
            blog_ingredients=data.get('blog_ingredients'),
            blog_description=data.get('blog_description'),
            likes=data.get('likes', 0),  # Default likes to 0 if not provided
            timestamp=datetime.utcnow()
        )
        
        # Add the new recipe to the session and commit
        db.session.add(new_recipe)
        db.session.commit()
        
        # Return a success message
        return jsonify({"message": "Recipe inserted successfully."}), 201
    except Exception as e:
        # For any error, rollback the session and return an error message
        db.session.rollback()
        return jsonify({"error": "An error occurred while inserting the recipe.", "details": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
    