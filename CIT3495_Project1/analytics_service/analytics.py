from flask import Flask, jsonify
import pymysql
import pymongo
import os
import time

app = Flask(__name__)

# MySQL configuration
MYSQL_HOST = os.getenv("MYSQL_HOST", "mysql_db")
MYSQL_USER = os.getenv("MYSQL_USER", "user")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "password")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "data_collection")

# MongoDB configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo_db:27017/analytics")
mongo_client = pymongo.MongoClient(MONGO_URI)
mongo_db = mongo_client["analytics"]


# Function to connect to MySQL with retry mechanism
def get_mysql_connection(retries=5, delay=5):
    for i in range(retries):
        try:
            print(f"Connecting to MySQL (Attempt {i+1}/{retries})...")
            conn = pymysql.connect(
                host=MYSQL_HOST,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                database=MYSQL_DATABASE,
                connect_timeout=10,
            )
            print("Connected to MySQL successfully!")
            return conn
        except pymysql.err.OperationalError as e:
            print(f"MySQL connection failed: {e}")
            if i < retries - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("Failed to connect to MySQL after multiple attempts.")
                raise


# Function to fetch analytics and update MongoDB
def update_analytics():
    mysql_conn = get_mysql_connection()
    cursor = mysql_conn.cursor()

    # Correct query to fetch data from "user_input" column in "entries" table
    cursor.execute(
        "SELECT MAX(user_input), MIN(user_input), AVG(user_input) FROM entries"
    )
    result = cursor.fetchone()

    print(f"DEBUG: Fetched from MySQL → {result}")  # Debugging output

    if result:
        max_val, min_val, avg_val = result

        # Only update MongoDB if there is valid data
        if max_val is not None and min_val is not None and avg_val is not None:
            print(
                f"DEBUG: Inserting into MongoDB → Max: {max_val}, Min: {min_val}, Avg: {avg_val}"
            )
            mongo_db.stats.update_one(
                {},
                {"$set": {"max": max_val, "min": min_val, "avg": avg_val}},
                upsert=True,
            )
            print("Analytics updated in MongoDB")
        else:
            print("DEBUG: MySQL returned NULL values.")
    else:
        print("No data found in MySQL.")

    cursor.close()
    mysql_conn.close()


# API Endpoint to manually trigger analytics update
@app.route("/update-analytics", methods=["POST"])
def trigger_update():
    update_analytics()
    return jsonify({"message": "Analytics updated successfully"}), 200


# API Endpoint to retrieve analytics data
@app.route("/analytics", methods=["GET"])
def get_analytics():
    stats = mongo_db.stats.find_one({}, {"_id": 0})  # Exclude MongoDB _id field
    if stats:
        return jsonify(stats)
    return jsonify({"error": "No analytics found"}), 404


# Run Flask Server to Keep the Service Running
if __name__ == "__main__":
    update_analytics()  # Run once on startup
    app.run(
        host="0.0.0.0", port=5003, debug=True
    )  # Ensure Flask server runs continuously
