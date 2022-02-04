from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from passlib.hash import argon2

# Create a blueprint object that can be used as an app object for this blueprint
from rsa.rsa import generate_rsa_pair

bp_open = Blueprint('bp_open', __name__)


@bp_open.get('/')
def index():
    return render_template("index.html")


@bp_open.post('/sign_in')
def sign_in():

    email = request.form["email"]
    password = request.form["password"]
    user = User.query.filter_by(email=email).first()
    try:
        if user is None:
            flash('Wrong email or password')
            return redirect(url_for('bp_open.index'))

        if not argon2.verify(password, user.password):
            flash('Wrong email or password')
            return redirect(url_for('bp_open.index'))
    except ValueError:
        # Caused be previous users using sha256 password hash
        flash("Something went wrong")
        return redirect(url_for('bp_open.index'))

    login_user(user)

    return redirect(url_for('bp_user.user_get'))


@bp_open.get('/signup')
def signup_get():
    return render_template("sign_up.html")


@bp_open.post('/signup')
def signup_post():
    email = request.form.get('email')
    username = request.form.get('user_name')
    password = request.form['password']
    hashed_password = argon2.using(rounds=10).hash(password)

    # Check if user with this password exists in the database
    user = User.query.filter_by(email=email).first()  # First will give us an object if user exist, or None if not

    if user:
        # If user is not none, then a user with this email exists in the database
        flash("Email address is already in use")
        return redirect(url_for('bp_open.signup_get'))

    user_public_key = generate_rsa_pair(username)

    new_user = User(name=username, email=email, password=hashed_password, public_rsa_key=user_public_key)

    from app import db
    db.session.add(new_user)
    db.session.commit()

    login_user(new_user)

    return redirect(url_for('bp_user.user_get'))
