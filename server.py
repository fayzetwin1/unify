from flask import Flask, request, jsonify, session
from flask_socketio import SocketIO, send, emit
from flask_sqlalchemy import SQLAlchemy
import logging
import re
from datetime import datetime
import bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
socketio = SocketIO(app, logger=True, engineio_logger=True, manage_session=False)

logging.basicConfig(level=logging.DEBUG)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

with app.app_context():
    db.create_all()

def is_valid_username(username):
    return re.match(r'^[a-zA-Z0-9]{1,24}$', username) is not None

def is_valid_password(password):
    return re.match(r'^[a-zA-Z0-9]{6,128}$', password) is not None

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(password, password_hash):
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

@app.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')
    if not is_valid_username(username):
        return jsonify({"message": "Invalid username"}), 400
    if not is_valid_password(password):
        return jsonify({"message": "Invalid password"}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists"}), 400
    password_hash = hash_password(password)
    new_user = User(username=username, password_hash=password_hash.decode('utf-8'))
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User created successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    user = User.query.filter_by(username=username).first()
    if user and check_password(password, user.password_hash):
        session['username'] = username
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"message": "Bad username or password"}), 401

@socketio.on('connect')
def handle_connect():
    if 'username' not in session:
        return False
    logging.debug("Client connected")

@socketio.on('disconnect')
def handle_disconnect():
    logging.debug("Client disconnected")

@socketio.on('message')
def handle_message(data):
    if 'username' not in session:
        logging.error("Authorization error: Missing session information")
        return
    username = session['username']
    timestamp = datetime.now().strftime('%H:%M:%S')
    message = data.get('message')
    token = data.get('token')
    if not token or token != app.config['SECRET_KEY']:
        logging.error("Authorization error: Invalid token")
        return
    logging.debug(f"Received message from {username}: {message}")
    emit('message', {'user': username, 'message': message, 'timestamp': timestamp}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)