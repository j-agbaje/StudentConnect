import eventlet
eventlet.monkey_patch()
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



# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'site.db')

app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

# Load configuration from config.json
with open('config.json') as config_file:
    config_data = json.load(config_file)
    mail_config = config_data.get('mail', {})
    redis_config = config_data.get('redis', {})
    elasticsearch = config_data.get('elasticsearch', {})

    # Mail settings
    app.config['MAIL_SERVER'] = mail_config.get('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = mail_config.get('MAIL_PORT', 587)
    app.config['MAIL_USE_TLS'] = mail_config.get('MAIL_USE_TLS', True)
    app.config['MAIL_USERNAME'] = mail_config.get('MAIL_USERNAME')
    app.config['MAIL_DEFAULT_SENDER'] = mail_config.get('MAIL_DEFAULT_SENDER')

    # Redis settings
    app.config['REDIS_HOST'] = redis_config.get('REDIS_HOST', 'localhost')
    app.config['REDIS_PORT'] = redis_config.get('REDIS_PORT', 6379)

    app.config['ELASTISEARCH_URL'] = elasticsearch.config.get('elastisearch_url')
    app.config['API_KEY'] = elasticsearch.config.get('api_key')
    app.config['CLOUD_ID'] = elasticsearch.config.get('clound_id')


# Redis URL for SocketIO
redis_url = f"redis://{app.config['REDIS_HOST']}:{app.config['REDIS_PORT']}/0"

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'primary'
migrate = Migrate(app, db)
CORS(app)
socketio = SocketIO(app, message_queue=redis_url, cors_allowed_origins="*", async_mode='eventlet')
mail = Mail(app)

# Logging setup
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(level=getattr(logging, log_level))

from StudentConnect import routes  # Avoid circular imports
