from flask import Blueprint, render_template, redirect, url_for, flash, Response, request
from flask_login import logout_user, login_required, current_user

from controllers.message_controller import get_user_messages, create_message
from controllers.user_controller import get_user_by_id
from models import User

bp_user = Blueprint('bp_user', __name__)


@bp_user.get('/user-home-page')
@login_required
def user_get():
    users = User.query.all()
    from app import db
    current_user.signed_in = 1

    db.session.commit()
    return render_template("user_home_page.html", users_data=users)


@bp_user.get('/signout')
def sign_out():
    from app import db
    current_user.signed_in = 0

    db.session.commit()
    logout_user()
    return redirect(url_for('bp_open.index'))


@bp_user.get('/profile/<user_id>')
def get_user_profile(user_id):
    user_id = int(user_id)
    user = get_user_by_id(user_id)
    return render_template('user_profile.html', user=user)



@bp_user.get('/message/<user_id>')
def message_get(user_id):
    user_id = int(user_id)
    receiver = get_user_by_id(user_id)
    return render_template('message.html', receiver=receiver)


@bp_user.post('/message')
def message_post():
    title = request.form['title']
    body = request.form['body']
    receiver_id = request.form['user_id']
    create_message(title, body, receiver_id)
    return redirect(url_for('bp_user.user_get'))


@bp_user.get('/mailbox')
def mailbox_get():
    messages = get_user_messages()
    return render_template('mailbox.html', messages=messages)