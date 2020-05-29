from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField, TimeField, DateTimeField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
import phonenumbers
from passlib.hash import pbkdf2_sha256
from app.models import User
from flask_login import current_user

def invalid_credentials(form, field):

    password = form.password.data
    email = form.email.data

    # Check username is invalid
    user_data = User.query.filter_by(email=email).first()
    if user_data is None:
        raise ValidationError("Email or password is incorrect")

    # Check password in invalid
    elif not pbkdf2_sha256.verify(password, user_data.password):
        raise ValidationError("Email or password is incorrect")


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(message="Please enter a valid email address")])
    password = PasswordField('Password', validators=[DataRequired(), invalid_credentials])
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email(message="Please enter a valid email address")])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=2, max=10, message="Enter a valid Phone Number")])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=25, message="Password must be between 6 and 25 Characters")])
    confirm_pswd = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message="Passwords must match")])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user_object = User.query.filter_by(email=email.data).first()

        if user_object:
            raise ValidationError("User already exists.")

class EditForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email(message="Please enter a valid email address")])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=2, max=10, message="Enter a valid Phone Number")])
    submit = SubmitField('Save Changes')

    def validate_email(self, email):
        if email.data != current_user.email:
            user_object = User.query.filter_by(email=email.data).first()
            if user_object:
                raise ValidationError("User already exists.")

def pass_verify(form, field):
    password = form.old_pass.data;
    user_data = User.query.filter_by(id=current_user.id).first()
    if not pbkdf2_sha256.verify(password, user_data.password):
        raise ValidationError("Invalid Password")

class PassForm(FlaskForm):
    old_pass = PasswordField('Confirm Old Password', validators=[DataRequired(), pass_verify])
    new_pass = PasswordField('New Password', validators=[DataRequired(), Length(min=6, max=25, message="Password must be between 6 and 25 Characters")])
    confirm_pass = PasswordField('Retype Password', validators=[DataRequired(), EqualTo('new_pass', message="Passwords must match")])
    save = SubmitField('Save Changes')


class DoctorProfile(FlaskForm):
    name = StringField('Doctor\'s Name', validators=[DataRequired()])
    specialty = StringField('Speciality', validators=[DataRequired()])
    clinic_name = StringField('Clinic\'s Name', validators=[DataRequired()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=2, max=10, message="Enter a valid Phone Number")])
    location = StringField('Location', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    fees = StringField('Consultation Fees', validators=[DataRequired()])
    submit = SubmitField('Save Deatils')


class Search(FlaskForm):
    city = StringField('city')
    specialty = StringField('specialty')
    search = SubmitField('Search')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(message="Please enter a valid email address")])
    submit = SubmitField('Request Password Reset')

    def validate_email(self,email):
        user_object = User.query.filter_by(email=email.data).first()

        if not user_object:
            raise ValidationError("User does not exist.")

class ResetPasswordForm(FlaskForm):
    new_pass = PasswordField('New Password', validators=[DataRequired(), Length(min=6, max=25, message="Password must be between 6 and 25 Characters")])
    confirm_pass = PasswordField('Retype Password', validators=[DataRequired(), EqualTo('new_pass', message="Passwords must match")])
    save = SubmitField('Save Changes')
