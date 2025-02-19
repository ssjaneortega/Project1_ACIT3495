from flask import Flask, request, jsonify, render_template
import pymongo
import requests
import os

app = Flask(__name__)

# MongoDB configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo_db:27017/analytics")
mongo_client = pymongo.MongoClient(MONGO_URI)
mongo_db = mongo_client["analytics"]

# Authentication service URL
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth_service:5001")


# Authenticate user using the authentication service
def authenticate_user(username, password):
    auth_url = f"{AUTH_SERVICE_URL}/login"
    response = requests.post(
        auth_url, json={"username": username, "password": password}
    )
    if response.status_code == 200:
        return True
    return False


@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@app.route("/show-results", methods=["GET"])
def show_results():
    # Authenticate user from request (this can be session-based)
    username = request.args.get("username")
    password = request.args.get("password")

    # Authenticate user first
    if not authenticate_user(username, password):
        return jsonify({"error": "Unauthorized access"}), 401

    # Retrieve analytics data from MongoDB
    stats = mongo_db.stats.find_one()  # Assuming only one document with stats

    if stats:
        return render_template("results.html", stats=stats)
    return jsonify({"error": "No analytics found"}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3002, debug=True)
