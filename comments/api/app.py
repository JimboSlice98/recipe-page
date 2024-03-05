import pyodbc
from flask import Flask, request, jsonify, render_template, render_template_string
from dotenv import load_dotenv
import os, requests


load_dotenv()


app = Flask(__name__)


@app.route("/get-comments", methods=["GET"])
def get_comments():
    blog_id = request.args.get("blog_id")

    print(
        f"Driver   = {{{os.environ['COMMENTS_DRIVER']}}};\n"
        f"Server   = {os.environ['COMMENTS_SERVER']};\n"
        f"Database = {os.environ['COMMENTS_DATABASE']};\n"
        f"UID      = {os.environ['COMMENTS_USERNAME']};\n"
        f"PWD      = {os.environ['COMMENTS_PASSWORD']};\n"
        )

    try:
        conn_str = (
            f"Driver={{{os.environ['COMMENTS_DRIVER']}}};"
            f"Server={os.environ['COMMENTS_SERVER']};"
            f"Database={os.environ['COMMENTS_DATABASE']};"
            f"UID={os.environ['COMMENTS_USERNAME']};"
            f"PWD={os.environ['COMMENTS_PASSWORD']};"
        )
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        if blog_id:
            query = "SELECT comment_id, blog_id, time_stamp, user_id, message FROM Comments WHERE blog_id = ?"
            params = (blog_id,)
        else:
            query = "SELECT comment_id, blog_id, time_stamp, user_id, message FROM Comments"
            params = ()

        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        comments_data = [
            {
                "comment_id": row.comment_id, 
                "blog_id": row.blog_id, 
                "time_stamp": row.time_stamp,
                "user_id": row.user_id, 
                "message": row.message
            } 
            for row in rows
        ]
        
        if comments_data:
            return jsonify(comments_data)
        else:
            return jsonify({"error": "No comments found"}), 404

    except pyodbc.Error as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500


@app.route("/submit-comment", methods=["POST"])
def submit_comment():
    data = request.json
    comment_id = data.get("comment_id")
    time_stamp = data.get("time_stamp")
    blog_id = data.get("blog_id")
    user_id = data.get("user_id")
    message = data.get("message")
    
    if not all([comment_id, time_stamp, blog_id, user_id, message]):
        return jsonify({"error": "Missing required fields"}), 400
    
    try:
        conn_str = (
            f"Driver={{{os.environ['COMMENTS_DRIVER']}}};"
            f"Server={os.environ['COMMENTS_SERVER']};"
            f"Database={os.environ['COMMENTS_DATABASE']};"
            f"UID={os.environ['COMMENTS_USERNAME']};"
            f"PWD={os.environ['COMMENTS_PASSWORD']};"
        )
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        query = "INSERT INTO Comments (comment_id, time_stamp, blog_id, user_id, message) VALUES (?, ?, ?, ?, ?)"
        cursor.execute(query, (comment_id, time_stamp, blog_id, user_id, message))
        conn.commit()
        
        return jsonify({"success": "Comment submitted successfully"}), 201

    except pyodbc.Error as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500


@app.route("/new-comment", methods=["GET"])
def new_comment():
    # HTML form with JavaScript to submit form data as JSON
    form_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Submit Comment</title>
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    </head>
    <body>
        <h2>Submit New Comment</h2>
        <form id="commentForm">
            Comment ID: <input type="text" name="comment_id"><br>
            Time Stamp: <input type="text" name="time_stamp"><br>
            Blog ID: <input type="number" name="blog_id"><br>
            User ID: <input type="number" name="user_id"><br>
            Message: <textarea name="message"></textarea><br>
            <input type="submit" value="Submit Comment">
        </form>

        <script>
            $("#commentForm").submit(function(event) {
                event.preventDefault(); // Prevent the form from submitting via the browser
                var formData = $(this).serializeArray();
                var jsonData = {};
                $.each(formData, function() {
                    jsonData[this.name] = this.value || '';
                });
                $.ajax({
                    url: "/submit-comment",
                    type: "POST",
                    contentType: "application/json",
                    data: JSON.stringify(jsonData),
                    success: function(response) {
                        alert("Comment submitted successfully!");
                    },
                    error: function(xhr, status, error) {
                        alert("Error submitting comment: " + xhr.responseText);
                    }
                });
            });
        </script>
    </body>
    </html>
    """
    return render_template_string(form_html)


@app.route("/", methods=["GET"])
def root():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
