from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Hardcoded data for demonstration purposes
users_settings = {
    "1": {"user_id": "1", "cooking_level": "Expert Chef", "birthday": "1990-01-01"},
    "2": {"user_id": "2", "cooking_level": "Novice", "birthday": "1992-02-02"},
    # Add more user settings as needed
}

@app.route("/get-user-settings", methods=["POST"])
def get_user_settings():
    data = request.json
    user_id = data.get("user_id")
    user_settings = users_settings.get(user_id)

    if user_settings:
        return jsonify(user_settings)
    else:
        return jsonify({"error": "User not found"}), 404
    
@app.route("/home", methods=["GET"])
def home():
    # return index 1
    return render_template("index.html")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

