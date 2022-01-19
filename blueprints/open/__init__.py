from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import User

# Create a blueprint object that can be used as an app object for this blueprint
bp_open = Blueprint('bp_open', __name__)


@bp_open.get('/')
def index():
    return render_template("index.html")


@bp_open.post('/authenticate')
def authenticate_post():
    username = request.form["user_name"]
    password = request.form["password"]
    user = User.query.filter_by(name=username).first()

    if user:
        if check_password_hash(user.password, password):
            return redirect(url_for('bp_open.user_login'))

    flash("User or password incorrect")
    return redirect(url_for('bp_open.index'))


@bp_open.get('/signup')
def create_user_get():
    return render_template("sign_up.html")


@bp_open.get('/authenticate/login')
def user_login():
    return render_template("login.html")


@bp_open.post('/signup')
def signup_post():
    email = request.form.get('email')
    username = request.form.get('user_name')
    password = request.form['password']
    hashed_password = generate_password_hash(password, method='sha256')

    # Check if user with this password exists in the database
    user = User.query.filter_by(email=email).first()  # First will give us an object if user exist, or None if not

    if user:
        # If user is not none, then a user with this email exists in the database
        flash("Email address is already in use")
        return redirect(url_for('bp_open.create_user_get'))

    new_user = User(name=username, email=email, password=hashed_password)

    from app import db
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('bp_open.user_login'))