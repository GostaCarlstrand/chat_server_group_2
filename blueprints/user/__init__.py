import json
import os
from functools import wraps

from flask import Blueprint, render_template, redirect, url_for, flash, Response, request
from flask_login import logout_user, login_required, current_user
from flask_cors import CORS, cross_origin
from controllers.chat_controller import create_chat_request, get_user_chat_requests, accept_chat_request
from controllers.message_controller import get_user_messages, create_message, get_all_messages
from controllers.user_controller import get_user_by_id
from models import User, Chat

bp_user = Blueprint('bp_user', __name__)


@bp_user.get('/check_incoming_chats')
@cross_origin()
@login_required
def check_incoming_chats():
    # Check for incoming chats from db for current_user
    from models import Chat
    count = 0
    incoming_chats = Chat.query.filter_by(receiver_id=current_user.id).all()
    for chat in incoming_chats:
        if not chat.user_b_accepted:
            count += 1
    chats = {
        "newChats": count
    }
    return Response(json.dumps(chats), 200, content_type='application/json')


@bp_user.get('/check_accepted_chats')
@cross_origin()
@login_required
def check_accepted_chats():
    # Check for accepted chats from db for current_user
    from models import Chat
    count = 0
    accepted_chats = Chat.query.filter_by(sender_id=current_user.id).all()
    for chat in accepted_chats:
        if chat.user_b_accepted:
            count += 1
    chats = {
        "newChats": count
    }
    return Response(json.dumps(chats), 200, content_type='application/json')


@bp_user.get('/check_messages')
@cross_origin()
@login_required
def check_messages():
    # Check for messages from db for current_user
    from app import db
    from models import User
    user = current_user
    count = 0
    for message in user.recv_messages:
        if not message.read:
            count += 1
    messages = {
        "newMessages": count
    }
    return Response(json.dumps(messages), 200, content_type='application/json')


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
@login_required
def message_post():
    title = request.form['title']
    body = request.form['body']
    receiver_id = request.form['user_id']
    create_message(title, body, receiver_id)
    return redirect(url_for('bp_user.user_get'))


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
    create_message('Chat request sent', 'Your request has been sent. Wait for a message with further instructions.'
                   , current_user.id)
    create_chat_request(user, receiver_id)
    return redirect(url_for('bp_user.mailbox_get'))


@bp_user.post('/chat_request/accept/<chat_id>')
@login_required
def accept_chat(chat_id):
    accept_chat_request(chat_id)
    create_message('Chat accepted', 'Start your client server.', current_user.id)
    chat = Chat.query.filter_by(id=chat_id).first()
    create_message(f'Chat accepted by {current_user.name}', 'Start your socket server.', chat.sender_id)
    return redirect(url_for('bp_user.mailbox_get'))


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
    public_key = user.public_rsa_key.decode("utf-8")
    return Response(json.dumps(public_key), 200, content_type='application/json')


# @bp_user.get('/user_pubkey/<user_id>')
# @login_required
# def get_user_public_key(user_id):
#     user = get_user_by_id(user_id)
#     public_key = user.public_rsa_key
#     return Response(public_key, 200, content_type='application/data')