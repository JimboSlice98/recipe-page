from sqlalchemy import create_engine, Column, Integer, String, Text, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

from datetime import datetime


# # Define the connection string
# USERNAME = os.environ.get('RECIPES_USERNAME')
# PASSWORD = os.environ.get('RECIPES_PASSWORD')
# SERVER = os.environ.get('RECIPES_SERVER')
# PORT = os.environ.get('RECIPES_PORT')
# DATABASE = os.environ.get('RECIPES_DATABASE')

RECIPES_USERNAME="citus"
RECIPES_SERVER="c-sse-recipes-cluster-db.jyler3dqxlnhb5.postgres.cosmos.azure.com"
RECIPES_PORT=5432
RECIPES_DATABASE="sse-recipes-cosmos-db"
RECIPES_PASSWORD="JYpzGMF*c7'=c}R"

# Construct the connection string
# connection_string = f'postgresql://{USERNAME}:{PASSWORD}@{SERVER}:{PORT}/{DATABASE}'
connection_string = f'postgresql://{RECIPES_USERNAME}:{RECIPES_PASSWORD}@{RECIPES_SERVER}:{RECIPES_PORT}/{RECIPES_DATABASE}'
print(connection_string)

# Create engine
engine = create_engine(connection_string)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Define the ORM model
Base = declarative_base()

class Blog(Base):
    __tablename__ = 'blogs_testing'
    blog_id = Column(String(50), primary_key=True)
    user_id = Column(Integer)
    blog_title = Column(String(255))
    blog_ingredients = Column(Text)
    blog_description = Column(Text)
    likes = Column(Integer)
    timestamp = Column(TIMESTAMP)

data  = [blog_id='user2332024-03-05T12:00:00', user_id=233, blog_title='Amazing Lasagna Recipe',
             blog_ingredients='1 tomato, 2 cups of flour, 3 eggs, 4 cups of cheese, 5 leaves of basil',
             blog_description='Slice the tomato, Mix flour and eggs, Layer the ingredients, Bake for 45 minutes',
             likes=0, timestamp=datetime(2024, 3, 5, 12, 0, 0)]
# Function to insert dummy data into the blogs_testing table
def insert_dummy_data(data):
    # Create a new session
    # session = Session()
    
    # Define the dummy data as Blog model instances
    blogs = [
        Blog(data),
        Blog(blog_id='22024-03-05T12:00:01', user_id=2, blog_title='Classic Chicken Parmesan',
             blog_ingredients='2 chicken breasts, 1 cup breadcrumbs, 1 egg, 2 cups marinara sauce',
             blog_description='Bread the chicken, Fry until golden, Top with sauce and cheese, Bake to melt cheese',
             likes=0, timestamp=datetime(2024, 3, 5, 12, 0, 1)),
        Blog(blog_id='22024-03-05T12:00:02', user_id=2, blog_title='Vegetarian Stir Fry Extravaganza',
             blog_ingredients='1 bell pepper, 100g tofu, 2 tbsp soy sauce, 1 cup broccoli',
             blog_description='Chop vegetables and tofu, Stir fry with soy sauce, Serve over rice',
             likes=0, timestamp=datetime(2024, 3, 5, 12, 0, 2)),
        Blog(blog_id='12024-03-05T12:00:03', user_id=1, blog_title='Ultimate Chocolate Cake',
             blog_ingredients='200g chocolate, 100g butter, 3 eggs, 150g sugar, 100g flour',
             blog_description='Melt chocolate and butter, Mix in eggs and sugar, Fold in flour, Bake for 30 minutes',
             likes=0, timestamp=datetime(2024, 3, 5, 12, 0, 3)),
        Blog(blog_id='12024-03-05T12:00:04', user_id=1, blog_title='Healthy Kale Smoothie',
             blog_ingredients='2 cups kale, 1 banana, 1 apple, 1 cup almond milk',
             blog_description='Chop fruits, Blend with kale and almond milk until smooth',
             likes=0, timestamp=datetime(2024, 3, 5, 12, 0, 4))
    ]
    
    try:
        # Add all the blog instances to the session
        session.add_all(blogs)
        
        # Commit the session to insert the data into the database
        session.commit()
        print("Data inserted successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")
        session.rollback()  # Rollback the session in case of error
    finally:
        # Close the session
        session.close()

# Call the function to insert the data
# if __name__ == "__main__":
#     insert_dummy_data()

# Function to select all and print
def select_all_blogs():
    # Create a new session
    session = Session()
    
    try:
        # Query all blogs
        blogs = session.query(Blog).all()
        
        # Print out each blog
        for blog in blogs:
            print(f"Blog ID: {blog.blog_id}, User ID: {blog.user_id}, Title: {blog.blog_title}, Likes: {blog.likes}, Timestamp: {blog.timestamp}")
            print(f"Ingredients: {blog.blog_ingredients}")
            print(f"Description: {blog.blog_description}\n")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the session
        session.close()

# Make sure to create the engine and session before calling this function
if __name__ == "__main__":
    select_all_blogs()

# # Create engine
# engine = create_engine(connection_string)

# # Create a session
# Session = sessionmaker(bind=engine)
# session = Session()

# # Define the ORM model
# Base = declarative_base()

# class Blog(Base):
#     __tablename__ = 'blogs_testing'

#     blog_id = Column(String(50), primary_key=True)
#     user_id = Column(Integer)
#     blog_title = Column(String(255))
#     blog_ingredients = Column(Text)
#     blog_description = Column(Text)
#     likes = Column(Integer)
#     timestamp = Column(TIMESTAMP)

# # Create the table
# Base.metadata.create_all(engine)

# # Close the session
# session.close()