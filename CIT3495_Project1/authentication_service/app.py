from flask import Flask, request, jsonify

app = Flask(__name__)

users = {
    "admin": "password123",
    "user": "mypassword"
}

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    
    if users.get(username) == password:
        return jsonify({"message": "Login successful"}), 200
    return jsonify({"message": "Invalid credentials"}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
