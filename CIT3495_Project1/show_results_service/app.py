from flask import Flask, request, jsonify, render_template
import pymongo
import os
import requests

app = Flask(__name__)

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo_db:27017/analytics")
mongo_client = pymongo.MongoClient(MONGO_URI)
mongo_db = mongo_client["analytics"]

# Authentication Service URL
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth_service:5001")


# Function to authenticate user
def authenticate_user(username, password):
    auth_url = f"{AUTH_SERVICE_URL}/login"
    response = requests.post(
        auth_url, json={"username": username, "password": password}
    )
    return response.status_code == 200


@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@app.route("/analytics", methods=["GET"])
def show_analytics():
    return render_template("analytics.html")


@app.route("/authenticate", methods=["POST"])
def authenticate():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if authenticate_user(username, password):
        return jsonify({"success": True}), 200
    return jsonify({"success": False}), 401


@app.route("/api/analytics", methods=["GET"])
def get_analytics():
    stats = mongo_db.stats.find_one({}, {"_id": 0})  # Exclude MongoDB _id field
    if stats:
        return jsonify(stats)
    return jsonify({"error": "No analytics found"}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3002, debug=True)
