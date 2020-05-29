from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
import os
from flask_mail import Mail

app = Flask(__name__)

mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 587,
    "MAIL_USE_TLS": True,
    "MAIL_USE_SSL": False,
    "MAIL_USERNAME": os.environ.get('EMAIL_USER'),
    "MAIL_PASSWORD": os.environ.get('EMAIL_PASSWORD')
}
app.config.update(mail_settings)
mail = Mail(app)

app.secret_key = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login = LoginManager(app)
login.init_app(app)
login.login_view = 'login'
login.login_message = 'Please login to view this page'

from app import routes, models
