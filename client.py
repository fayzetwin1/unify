import sys
import json
import os
from cryptography.fernet import Fernet
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QLineEdit, QPushButton, QVBoxLayout, QWidget, QLabel, QHBoxLayout, QMessageBox, QFileDialog
from PyQt5.QtCore import Qt, QMetaObject, Q_ARG, QEvent
from PyQt5.QtGui import QPalette, QColor
import socketio
import logging
import requests
import argparse

sio = socketio.Client()

SESSION_FILE = 'unifyData/session.enc'
KEY_FILE = 'unifyData/key.key'

def generate_key():
    key = Fernet.generate_key()
    with open(KEY_FILE, 'wb') as key_file:
        key_file.write(key)

def load_key():
    return open(KEY_FILE, 'rb').read()

def encrypt(data, key):
    f = Fernet(key)
    encrypted_data = f.encrypt(data.encode())
    return encrypted_data

def decrypt(encrypted_data, key):
    f = Fernet(key)
    decrypted_data = f.decrypt(encrypted_data).decode()
    return decrypted_data

class AuthWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Authorization')
        self.setGeometry(100, 100, 300, 200)

        # Main layout
        main_layout = QVBoxLayout()

        # Username
        self.username_label = QLabel('Username:', self)
        self.username_input = QLineEdit(self)
        main_layout.addWidget(self.username_label)
        main_layout.addWidget(self.username_input)

        # Password
        self.password_label = QLabel('Password:', self)
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        main_layout.addWidget(self.password_label)
        main_layout.addWidget(self.password_input)

        # Buttons
        button_layout = QHBoxLayout()
        self.login_button = QPushButton('Login', self)
        self.login_button.clicked.connect(self.login)
        self.register_button = QPushButton('Register', self)
        self.register_button.clicked.connect(self.register)
        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.register_button)
        main_layout.addLayout(button_layout)

        # Set central widget
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.show()

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        try:
            response = requests.post('http://localhost:5000/login', json={'username': username, 'password': password})
            if response.status_code == 200:
                self.save_session(username, password)
                self.close()
                messenger_window = MessengerWindow()
                app.messenger_window = messenger_window
                sio.connect('http://localhost:5000', transports=['websocket'], headers={'Cookie': response.headers.get('Set-Cookie')})
            else:
                QMessageBox.warning(self, 'Login Failed', response.json().get('message'))
        except Exception as e:
            QMessageBox.warning(self, 'Login Failed', str(e))

    def register(self):
        username = self.username_input.text()
        password = self.password_input.text()
        try:
            response = requests.post('http://localhost:5000/register', json={'username': username, 'password': password})
            if response.status_code == 201:
                QMessageBox.information(self, 'Registration Successful', 'User registered successfully')
            else:
                QMessageBox.warning(self, 'Registration Failed', response.json().get('message'))
        except Exception as e:
            QMessageBox.warning(self, 'Registration Failed', str(e))

    def save_session(self, username, password):
        if not os.path.exists('unifyData'):
            os.makedirs('unifyData')
        if not os.path.exists(KEY_FILE):
            generate_key()
        key = load_key()
        data = json.dumps({'username': username, 'password': password})
        encrypted_data = encrypt(data, key)
        with open(SESSION_FILE, 'wb') as f:
            f.write(encrypted_data)

    @staticmethod
    def load_session():
        if os.path.exists(SESSION_FILE):
            key = load_key()
            with open(SESSION_FILE, 'rb') as f:
                encrypted_data = f.read()
            data = decrypt(encrypted_data, key)
            data = json.loads(data)
            return data.get('username'), data.get('password')
        return None, None

class MessengerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.set_dark_theme()

    def initUI(self):
        self.setWindowTitle('Messenger')
        self.setGeometry(100, 100, 600, 400)

        # Main layout
        main_layout = QVBoxLayout()

        # Header
        header_layout = QHBoxLayout()
        header_label = QLabel('Unify Messenger', self)
        header_label.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        header_layout.addWidget(header_label)
        main_layout.addLayout(header_layout)

        # Message area
        self.text_area = QTextEdit(self)
        self.text_area.setReadOnly(True)
        self.text_area.setStyleSheet("font-size: 16px; color: white; background-color: #333;")
        main_layout.addWidget(self.text_area)

        # Input area
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit(self)
        self.input_field.setPlaceholderText('Type your message here...')
        self.input_field.setStyleSheet("font-size: 16px; color: white; background-color: #333;")
        self.input_field.installEventFilter(self)
        input_layout.addWidget(self.input_field)

        self.send_button = QPushButton('Send', self)
        self.send_button.setStyleSheet("font-size: 16px; color: white; background-color: #555;")
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)

        main_layout.addLayout(input_layout)

        # Set central widget
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.show()

    def send_message(self):
        message = self.input_field.text()
        if message:
            logging.debug(f"Sending message: {message}")
            sio.emit('message', {'message': message, 'token': 'your_secret_key'})
            self.input_field.clear()

    def append_message(self, data):
        logging.debug(f"Appending message: {data}")
        QMetaObject.invokeMethod(self.text_area, "append", Qt.QueuedConnection, 
                                 Q_ARG(str, f"[{data['timestamp']}] {data['user']}: {data['message']}"))

    def set_dark_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.black)
        self.setPalette(palette)

    def eventFilter(self, obj, event):
        if obj == self.input_field and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                self.send_message()
                return True
        return super().eventFilter(obj, event)

@sio.on('connect')
def on_connect():
    logging.debug("Connected to server")

@sio.on('disconnect')
def on_disconnect():
    logging.debug("Disconnected from server")

@sio.on('message')
def on_message(data):
    logging.debug(f"Received message: {data}")
    app.messenger_window.append_message(data)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Unify Messenger Client')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    app = QApplication(sys.argv)
    username, password = AuthWindow.load_session()
    if username and password:
        response = requests.post('http://localhost:5000/login', json={'username': username, 'password': password})
        if response.status_code == 200:
            messenger_window = MessengerWindow()
            app.messenger_window = messenger_window
            sio.connect('http://localhost:5000', transports=['websocket'], headers={'Cookie': response.headers.get('Set-Cookie')})
        else:
            auth_window = AuthWindow()
    else:
        auth_window = AuthWindow()
    sys.exit(app.exec_())