from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash
from models import User

# Create a blueprint object that can be used as an app object for this blueprint
bp_open = Blueprint('bp_open', __name__)


@bp_open.get('/authenticate')
def authenticate():
    return render_template("authenticate.html")


@bp_open.get('/create_user')
def user_post():
    return render_template("create_user.html")

@bp_open.post('/create_user')
def new_user():
    data = request.form
    first_name = data["first_name"]
    last_name = data["last_name"]
    password = data["password"]
    username = data["user_name"]

    return redirect(url_for('user_login'))


@bp_open.get('/authenticate/login')
def user_login():
    return render_template("login.html")


@bp_open.get('/authenticate/create_user')
def user_create_user():
    return render_template("create_user.html")


@bp_open.post('/signup')
def signup_post():
    name = request.form['name']
    email = request.form.get('email')
    password = request.form['password']
    hashed_password = generate_password_hash(password, method='sha256')

    # Check if user with this password exists in the database
    user = User.query.filter_by(email=email).first()  # First will give us an object if user exist, or None if not
    if user:
        # If user is not none, then a user with this email exists in the database
        flash("Email address is already in use")
        return redirect(url_for('bp_open.signup_get'))

    new_user = User(name=name, email=email, password=hashed_password)

    from app import db
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('bp_open.login_get'))