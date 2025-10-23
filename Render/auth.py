import os
from datetime import date

from flask import Blueprint, make_response, jsonify
from flask import render_template, request, url_for, redirect, flash, session
from flask_login import login_required, logout_user, current_user
import sqlite3
import API.user_api
from flask_login import login_user
import requests
from werkzeug.security import generate_password_hash
from email.mime.text import MIMEText
import smtplib, random, string

from DB.user_db import UserDB
from Objects.user import User


auth = Blueprint('auth', __name__)


@auth.route('/')
def home():
    return render_template('home.html')


@auth.route("/password-recovery", methods=['GET', 'POST'])
def password_recovery():
    if request.method == 'POST':

        username = request.form["username"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        if username != "" and new_password != "" and new_password == confirm_password:
            hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')

            try:
                with UserDB() as db:

                    user = db.get_user_by_username(username)

                    if user:

                        db.update_password(username, hashed_password)
                        flash('Your password has been updated successfully!', 'success')
                        return redirect(url_for('auth.login'))
                    else:
                        flash('Username not found!', 'danger')
                        return redirect(url_for('auth.password_recovery'))

            except sqlite3.Error as e:
                flash('An error occurred. Please try again.', 'danger')
                return redirect(url_for('auth.password_recovery'))

        else:
            flash('Passwords do not match or fields are empty. Please try again.', 'danger')
            return redirect(url_for('auth.password_recovery'))
    else:
        return render_template('password_recovery.html')


@auth.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if request.form["username"] != "" and request.form["password"] != "" and request.form["confirm_password"] == \
                request.form["password"]:
            username = request.form["username"]
            password = request.form["password"]
            email = request.form["email"]
        else:
            flash('Something went wrong. Please try again.', 'danger')
            return redirect(url_for('register'))
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        try:
            with UserDB() as db:
                db.create_user(username, email, hashed_password)
            return redirect(url_for('auth.success'))
        except sqlite3.IntegrityError:
            flash('Username or Email already exists!', 'danger')
            return redirect(url_for('auth.register'))
    else:
        return render_template('register.html')


@auth.route('/success')
def success():
    return render_template('success.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        credentials = {'username': username, 'password': password}
        response = requests.post(os.getenv('BASE_URL') + 'api/auth', json=credentials)
        if response.status_code == 200:
            user_dict = API.user_api.get_user_by_id(response.json()['user_id'])[0].json
            user = User.from_dict(user_dict)
            session['id'] = user.id
            session['username'] = user.username
            session['email'] = user.email
            login_user(user)
            token = response.json().get('token')
            response = make_response(redirect(url_for('auth.profile', id=current_user.id)))
            response.set_cookie('token', token, httponly=True, secure=True, samesite='Strict')
            return response
        else:
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))

    return render_template('login.html')


@auth.route('/profile/<int:id>')
@login_required
def profile(id):
    is_own_profile = current_user.id == id
    user_data = API.user_api.get_user_by_id(id)[0].json
    if 'id' not in session:
        flash('Please log in to access this page.', 'danger')
        return redirect(url_for('auth.login'))
    if user_data:
        return render_template('profile.html', is_own_profile=is_own_profile, user=user_data)
    else:
        flash('User not found', 'error')
        return redirect(url_for('auth.login'))


@auth.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    email = request.form.get('email')
    username = request.form.get('username')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    birthdate = request.form.get('birthdate')
    if birthdate > date.today().isoformat():
        flash("Birthdate cannot be in the future.", "error")
        return redirect(url_for('auth.profile', id=current_user.id))
    phone = request.form.get('phone')
    json = {'id': current_user.id, 'email': email, 'username': username, 'first_name': first_name,
            'last_name': last_name, 'birthdate': birthdate, 'phone_number': phone}
    response = requests.post(os.getenv('BASE_URL') + f'api/user/{current_user.id}', json=json)
    if response.status_code == 200:
        flash('Profile updated successfully!', 'success')
    return redirect(url_for('auth.profile', id=current_user.id))


@auth.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/send-code', methods=['POST'])
def send_code():
    data = request.get_json()
    to_addr = data.get('email')
    code = ''.join(random.choices(string.digits, k=6))
    subject = 'One-Time Verification Code for Taskly'
    mail_content = 'Hello! Your one-time verification code is: %s. Thank you for using Taskly!' % code
    from_addr='mit652.capstone.group1@gmail.com'
    password='xzwqnmdhnqlheyqb'
    smtp_server='smtp.gmail.com'

    msg = MIMEText(mail_content, 'plain', 'utf-8')
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Subject'] = subject

    try:
        with smtplib.SMTP(smtp_server, 587) as server:
            #server.set_debuglevel(1)
            server.starttls()
            server.login(from_addr, password)
            server.sendmail(from_addr, [to_addr], msg.as_string())

        return jsonify({"message": "Verification code sent."})
    except Exception as e:
        print(e)
        return jsonify({"message": "Failed to send email."}), 500