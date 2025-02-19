from flask import Flask, request, jsonify, render_template
import mysql.connector
import os

app = Flask(__name__)

# Database configuration
DB_HOST = os.getenv("DB_HOST", "mysql-db")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_NAME = os.getenv("DB_NAME", "data_collection")

# Connect to MySQL
def get_db_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/entries", methods=["GET"])
def show_entries():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM entries")
        results = cursor.fetchall()
        cursor.close()
        conn.close()

        entries = [{"id": row[0], "user_input": row[1]} for row in results]
        return render_template("entries.html", entries=entries)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/enter-data", methods=["POST"])
def enter_data():
    try:
        data = request.json
        user_input = data.get("input")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO entries (user_input) VALUES (%s)", (user_input,))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Data entered successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/entries", methods=["GET"])
def get_entries():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM entries")
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        entries = [{"id": row[0], "user_input": row[1]} for row in results]
        return jsonify(entries)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3001, debug=True)
