import pyodbc
import os
from dotenv import load_dotenv

load_dotenv()

# Establish a connection to the SQL Server database
conn_str = (
    f"Driver={{{os.environ['COMMENTS_DRIVER']}}};"
    f"Server={os.environ['COMMENTS_SERVER']};"
    f"Database={os.environ['COMMENTS_DATABASE']};"
    f"UID={os.environ['COMMENTS_USERNAME']};"
    f"PWD={os.environ['COMMENTS_PASSWORD']};"
)
conn = pyodbc.connect(conn_str)

# Cursor to execute SQL queries
cursor = conn.cursor()

# Dictionary containing comment data
comment_data = {
    '1232': {
        '2343243': {'user_id': '2', 'message': 'Wow, I love this lasagna recipe!'},
        '2343244': {'user_id': '455', 'message': 'This looks absolutely delicious!'}
    },
    '1233': {
        '2343245': {'user_id': '233', 'message': 'Chicken Parmesan is my favorite. Thanks for sharing!'},
        '2343246': {'user_id': '454', 'message': 'I must try this over the weekend.'}
    },
    # Continue with the rest of your data...
}

# Assume that users and blogs need to be inserted beforehand
# This is a simplistic approach; in a real scenario, you would check if the records already exist

# Insert users (simplified; adjust as needed)
user_ids = set([comment_info['user_id'] for comments in comment_data.values() for comment_id, comment_info in comments.items()])
for user_id in user_ids:
    cursor.execute("""
        MERGE INTO Users AS target
        USING (SELECT ? AS user_id, ? AS username) AS source
        ON target.user_id = source.user_id
        WHEN NOT MATCHED THEN
            INSERT (user_id, username) VALUES (source.user_id, source.username);
    """, user_id, f"user{user_id}")

# Insert blogs (simplified; adjust as needed)
blog_ids = comment_data.keys()
for blog_id in blog_ids:
    cursor.execute("""
        MERGE INTO Blogs AS target
        USING (SELECT ? AS blog_id, ? AS title) AS source
        ON target.blog_id = source.blog_id
        WHEN NOT MATCHED THEN
            INSERT (blog_id, title) VALUES (source.blog_id, source.title);
    """, blog_id, f"Blog Title {blog_id}")


# Insert comments
for blog_id, comments in comment_data.items():
    for comment_id, comment_info in comments.items():
        user_id = comment_info['user_id']
        message = comment_info['message']
        
        cursor.execute(
            "INSERT INTO Comments (comment_id, blog_id, user_id, message) VALUES (?, ?, ?, ?)",
            comment_id, blog_id, user_id, message
        )

# Commit the transaction
conn.commit()

# Close the cursor and connection
cursor.close()
conn.close()

print("Data inserted successfully.")
