from flask import Flask, render_template, flash, redirect, url_for, request, abort
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import pbkdf2_sha256
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from app import app, db, login
from app.form import *
from app.models import *
import os
from werkzeug.urls import url_parse
from datetime import datetime
from app.email import send_password_reset_email

@app.route('/', methods=['GET','POST'])
def index():
    return render_template('index.html')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        flash("{} already logged in".format(current_user.firstname))
        return redirect(url_for('index'))

    login_form = LoginForm()

    if login_form.validate_on_submit():
        user_object = User.query.filter_by(email=login_form.email.data).first()
        login_user(user_object)

        next_page = request.args.get('next')
        if next_page:
            return redirect("next_page")
        flash('Login Successful for user {}'.format(login_form.email.data))
        return redirect(url_for('index'))

    return render_template('login.html', form=login_form)

@app.route('/logout')
@login_required
def logout():

    logout_user()
    flash("You have logged out successfully")
    return redirect(url_for('index'))

@app.route('/register/doctor', methods=['GET','POST'])
def doc_register():
    doc_form = RegistrationForm()

    if doc_form.validate_on_submit():
        firstname = doc_form.firstname.data
        lastname = doc_form.lastname.data
        email = doc_form.email.data
        phone = doc_form.phone.data
        password = doc_form.password.data

        hashed_pswd = pbkdf2_sha256.hash(password)

        user = User(firstname=firstname, lastname=lastname, email=email, phone=phone, password=hashed_pswd, role=2)
        db.session.add(user)
        db.session.commit()
        flash('{} registered Successfully'.format(doc_form.firstname.data))
        return redirect(url_for('login'))

    return render_template('doctor-register.html', form=doc_form)


@app.route('/register/patient', methods=['GET','POST'])
def patient_register():
    pat_form = RegistrationForm()

    if pat_form.validate_on_submit():
        firstname = pat_form.firstname.data
        lastname = pat_form.lastname.data
        email = pat_form.email.data
        phone = pat_form.phone.data
        password = pat_form.password.data

        hashed_pswd = pbkdf2_sha256.hash(password)

        user = User(firstname=firstname, lastname=lastname, email=email, phone=phone, password=hashed_pswd, role=1)
        db.session.add(user)
        db.session.commit()

        flash('{} registered Successfully'.format(pat_form.firstname.data))
        return redirect(url_for('login'))

    return render_template('patient-register.html',form=pat_form)

@app.route('/edit/details', methods=['GET','POST'])
@login_required
def edit_details():
    edit_form = EditForm()
    if edit_form.validate_on_submit():
        user_object = User.query.filter_by(id=current_user.id).first()

        user_object.firstname = edit_form.firstname.data
        user_object.lastname = edit_form.lastname.data
        user_object.email = edit_form.email.data
        user_object.phone = edit_form.phone.data

        print(f'\n{user_object.phone}\n')

        db.session.commit()

        print(f'\n{user_object.phone}\n')

        flash('Your changes have been saved.')
        return redirect(url_for('edit_details'))

    elif request.method == 'GET':
        edit_form.firstname.data = current_user.firstname
        edit_form.lastname.data = current_user.lastname
        edit_form.email.data = current_user.email
        edit_form.phone.data = current_user.phone

    return render_template('edit-details.html', form=edit_form)

@app.route('/change/password', methods=['GET','POST'])
@login_required
def change_password():
    change_form = PassForm()
    if change_form.validate_on_submit():

        hashed_pswd = pbkdf2_sha256.hash(change_form.new_pass.data)

        current_user.password = hashed_pswd
        db.session.commit()

        flash('Password changed successfully.')
        return redirect(url_for('index'))

    return render_template('change-password.html', form=change_form)

@app.route('/clinic', methods=['GET','POST'])
@login_required
def add_clinic():
    if current_user.role == 1:
        abort(404, description="Page not found")
    profile_form = DoctorProfile()

    profile = current_user.profile.first()
    if profile_form.validate_on_submit():
        name = profile_form.name.data
        specialty = profile_form.specialty.data
        clinic_name = profile_form.clinic_name.data
        phone = profile_form.phone.data
        location = profile_form.location.data
        city = profile_form.city.data
        fees = profile_form.fees.data

        profile = Doctor(name=name, specialty=specialty, clinic_name=clinic_name, phone=phone, location=location, city=city, fees=fees, user_id=current_user.id)
        if current_user.role == 2:
            current_user.role = 3
            db.session.add(profile)
        db.session.commit()

        flash("Changes Saved Successfully.")
        return redirect(url_for('add_clinic'))

    elif request.method == 'GET' and profile:
        profile = current_user.profile.first()
        profile_form.name.data = profile.name
        profile_form.specialty.data = profile.specialty
        profile_form.clinic_name.data = profile.clinic_name
        profile_form.phone.data = profile.phone
        profile_form.location.data = profile.location
        profile_form.city.data = profile.city
        profile_form.fees.data = profile.fees

    return render_template('add-clinic.html', form=profile_form)

@app.route('/search/doctor')
def search_doctor():
    search_form = Search()
    page = request.args.get('page', 1, type=int)
    city = request.args.get('city',type=str)
    specialty = request.args.get('specialty',type=str)

    if not city and not specialty:
        posts = Doctor.query.paginate(page=page, per_page=10)
    elif not city:
        posts = Doctor.query.filter_by(specialty=specialty).paginate(page=page, per_page=10)
    elif not specialty:
        posts = Doctor.query.filter_by(city=city).paginate(page=page, per_page=10)
    else:
        posts = Doctor.query.filter_by(specialty=specialty).filter_by(city=city)\
        .paginate(page=page, per_page=10)

    search_form.city.data = city
    search_form.specialty.data = specialty
    return render_template('search-doctor.html',posts=posts, form=search_form)

@app.route('/book_appointment/<id>')
@login_required
def book_appointment(id):
    date = request.args.get('date')
    time = request.args.get('time')
    if not date and not time:
        profile = Doctor.query.filter_by(id=id).first()
        return render_template('book-appointment.html',profile=profile)

    appointment = Appointments(user_id=current_user.id, doctor_id=id, date=date, time=time)
    db.session.add(appointment)
    db.session.commit()

    flash('Appointment Booked Successfully')
    return redirect(url_for('index'))

@app.route('/my/appointments')
@login_required
def my_appointment():
    page = request.args.get('page', 1, type=int)
    appointments = Appointments.query.filter_by(user_id=current_user.id)\
        .order_by(Appointments.date.desc())\
        .order_by(Appointments.time.asc())\
        .paginate(page=page, per_page=10)
    return render_template('my-appointment.html', appointments=appointments)

@app.route('/my/schedule')
@login_required
def my_schedule():
    if current_user.role == 1:
        abort(404, description="Page not found")

    page = request.args.get('page', 1, type=int)
    profile = current_user.profile.first()
    if not profile:
        abort(404, description="Page not found")
    appointments = Appointments.query.filter_by(doctor_id=profile.id)\
        .order_by(Appointments.date.desc())\
        .order_by(Appointments.time.asc())\
        .paginate(page=page, per_page=10)
    return render_template('my-schedule.html', appointments=appointments)

@app.route('/forgot_password', methods=['GET','POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)

        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('forgot-password.html',form=form)

@app.route('/reset_password/<token>', methods=['GET','POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_pswd = pbkdf2_sha256.hash(form.new_pass.data)
        user.password = hashed_pswd
        db.session.commit()
        flash('Your password had been reset.')
        return redirect(url_for('login'))
    return render_template('reset-password.html', form=form, token=token)
