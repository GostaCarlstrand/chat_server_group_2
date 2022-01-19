from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash

from models import User

bp_open = Blueprint('bp_open', __name__)


@bp_open.get('/authenticate')
def authenticate_get():
    return render_template("authenticate.html")


@bp_open.post('/authenticate')
def authenticate_post():
    email = request.form['user_name']
    password = request.form['password']

    # Check if user with this password exists in the database
    user = User.query.filter_by(email=email).first()  # First will give us an object if user exists, or None if not
    if user:
        if check_password_hash(user.password, password):
            # User with this email and password exists
            return redirect(url_for('bp_user.user_home_get'))
    return render_template("unauthorized.html")


@bp_open.get('/authenticate/login')
def login_get():
    return render_template("user_home.html")


@bp_open.get('/authenticate/signup')
def signup_get():
    return render_template("signup.html")


@bp_open.post('/authenticate/signup')
def signup_post():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    hashed_password = generate_password_hash(password, method='sha256')

    # Check if user with this password exists in the database
    user = User.query.filter_by(email=email).first()  # First will give us an object if user exists, or None if not
    if user:
        # User with this email exists
        flash("Email address already in use.")
        return redirect(url_for('bp_open.signup_get'))

    new_user = User(name=name, email=email, password=hashed_password)

    from app import db
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('bp_open.login_get'))