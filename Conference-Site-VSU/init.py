from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO

from config import Config

application = Flask(__name__)
application.config.from_object(Config)
login = LoginManager(application)
login.login_view = 'login'
db = SQLAlchemy(application)
migrate = Migrate(application, db)
socketio = SocketIO()
socketio.init_app(application)