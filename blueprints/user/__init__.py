import json
import os
from functools import wraps

from flask import Blueprint, render_template, redirect, url_for, flash, Response, request
from flask_login import logout_user, login_required, current_user

from controllers.chat_controller import create_chat_request, get_user_chat_requests, accept_chat_request
from controllers.message_controller import get_user_messages, create_message, get_all_messages
from controllers.user_controller import get_user_by_id
from models import User, Chat

bp_user = Blueprint('bp_user', __name__)


def authorize_admin(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        is_admin = current_user.admin
        if not is_admin:
            response = {
                'Result': "You're not authorized!",
                'Reason': 'Not an admin.'
            }
            return Response(json.dumps(response), 401, content_type='application/json')
        return f(*args, **kwargs)
    return wrapper


@bp_user.get('/user-home-page')
@login_required
def user_get():
    users = User.query.all()
    from app import db
    current_user.signed_in = 1

    db.session.commit()
    return render_template("user_home_page.html", users_data=users)


@bp_user.get('/signout')
@login_required
def sign_out():
    from app import db
    current_user.signed_in = 0

    db.session.commit()
    logout_user()
    return redirect(url_for('bp_open.index'))


@bp_user.get('/profile/<user_id>')
@login_required
def get_user_profile(user_id):
    user_id = int(user_id)
    user = get_user_by_id(user_id)
    chat_request = get_user_chat_requests(user_id)

    return render_template('user_profile.html', user=user, chat_requests=chat_request)


@bp_user.post('/message')
def message_post():
    data = request.json
    title = data['title']
    body = data['body']
    encrypted_aes_key = data['aes_key']
    receiver_id = data['user_id']
    create_message(title, body, receiver_id, encrypted_aes_key)
    return redirect(url_for('bp_user.user_get'))

@bp_user.get('/messages')
def user_msg_js():
    messages = get_user_messages()
    message_to_mailbox = []
    for message in messages:
        message_dict = {
            'title': message.title,
            'body': message.body,
            'encrypted_aes_key': message.encrypted_aes_key,
            'sender_id': message.sender_id
        }
        message_to_mailbox.append(message_dict)
    return Response(json.dumps(message_to_mailbox), 200, content_type='application/json')


@bp_user.get('/mailbox')
@login_required
def mailbox_get():
    messages = get_user_messages()
    return render_template('mailbox.html', messages=messages)


@bp_user.post('/chat_request')
@login_required
def send_chat_request():
    receiver_id = request.form['user_id']
    user = current_user.id
    create_chat_request(user, receiver_id)
    return redirect(url_for('bp_user.user_get'))


@bp_user.post('/chat_request/accept/<chat_id>')
@login_required
def accept_chat(chat_id):
    accept_chat_request(chat_id)
    create_message('Chat accepted', 'Start your client server.', current_user.id)
    chat = Chat.query.filter_by(id=chat_id).first()
    create_message(f'Chat accepted by {current_user.name}', 'Start your socket server.', chat.sender_id)
    return redirect(url_for('bp_user.user_get'))


@bp_user.get('/admin')
@login_required
@authorize_admin
def get_admin_all_messages():
    messages = get_all_messages()
    return render_template('admin.html', messages=messages)


@bp_user.get('/user_pubkey/<user_id>')
@login_required
def get_user_public_key(user_id):
    user = get_user_by_id(user_id)
    public_key = user.public_rsa_key.decode("utf-8")    #Only arne have pub key

    return Response(json.dumps(public_key), 200, content_type='application/json')