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

    cursor.execute("SELECT MAX(user_input), MIN(user_input), AVG(user_input) FROM entries")
    result = cursor.fetchone()

    if result and all(r is not None for r in result):  # Ensure no NULL values
        max_val, min_val, avg_val = result
        stats_collection = mongo_db.get_collection('stats')

        # Convert Decimal to float for avg_val
        avg_val = float(avg_val)

        stats_collection.insert_one({
            "max": max_val,
            "min": min_val,
            "avg": avg_val
        })

        print(f"Updated MongoDB: Max={max_val}, Min={min_val}, Avg={avg_val}")
    else:
        print("No valid data found in MySQL.")

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
