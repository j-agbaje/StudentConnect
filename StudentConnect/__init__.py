from StudentConnect.config import Config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_mail import Mail
import logging
import redis
from dotenv import load_dotenv
import json



import os
load_dotenv()


# Initialize the Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = '7e0877de3357eaa226c1ee00d041e839'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'site.db')




app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')  # Retrieved from .env
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')


with open('config.json') as config_file:
    config_data = json.load(config_file)
    app.config['MAIL_SERVER'] = config_data['mail']['MAIL_SERVER']
    app.config['MAIL_PORT'] = config_data['mail']['MAIL_PORT']
    app.config['MAIL_USE_TLS'] = config_data['mail']['MAIL_USE_TLS']
    app.config['MAIL_USERNAME'] = config_data['mail']['MAIL_USERNAME']
    app.config['MAIL_PASSWORD'] = config_data['mail']['MAIL_PASSWORD']
    app.config['MAIL_DEFAULT_SENDER'] = config_data['mail']['MAIL_DEFAULT_SENDER']

# Initialize the database
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'primary'
migrate = Migrate(app, db)

CORS(app)
socketio = SocketIO(app, message_queue='redis://localhost:6379/0', cors_allowed_origins="*", async_mode='eventlet')
mail = Mail(app)

logging.basicConfig(level=logging.INFO)


from StudentConnect import routes   #Avoiding circular imports