from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import logout_user, login_required, current_user
import requests

from models import User

bp_user = Blueprint('bp_user', __name__)


@bp_user.get('/user-home-page')
@login_required
def user_get():
    users = User.query.all()
    from app import db
    current_user.admin = True
    db.session.commit()
    return render_template("user_home_page.html", users_data=users)


@bp_user.get('/signout')
def sign_out():
    from app import db
    current_user.admin = False
    db.session.commit()
    logout_user()
    return redirect(url_for('bp_open.index'))


@bp_user.get('/request_<user>_ip_address')
def request_user_ip(user):
    r = requests.get((url_for('bp_user.return_user_ip')), params=user)


@bp_user.get('/get_user_ip')
def return_user_ip():
    pass