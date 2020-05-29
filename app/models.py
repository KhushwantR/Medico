from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from app import app,login, db
from time import time
import jwt

db = SQLAlchemy()

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(25), nullable=False)
    lastname = db.Column(db.String(25), nullable=False)
    email = db.Column(db.String(125), unique=True, nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    role = db.Column(db.Integer, nullable=False)
    profile = db.relationship('Doctor', backref='author', lazy='dynamic')
    appointment = db.relationship('Appointments', lazy='dynamic')

    def __init__(self, firstname, lastname, email, phone, password, role):
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.phone = phone
        self.password = password
        self.role = role

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return f"Name is {self.firstname}"

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode({'reset_password': self.id, 'exp':time() + expires_in}, app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token,app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

class Doctor(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialty = db.Column(db.String(50), nullable=False)
    clinic_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(25), nullable=False)
    fees = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    appointment = db.relationship('Appointments', backref='author', lazy='dynamic')


class Appointments(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    patient_name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(10), nullable=False)
    time = db.Column(db.String(10), nullable=False)
