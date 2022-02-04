import json
from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, Response, request, flash
from flask_login import logout_user, login_required, current_user
from flask_cors import cross_origin
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


def authorize_public_key(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        has_key_been_uploaded = current_user.public_rsa_key
        if not has_key_been_uploaded:
            response = {
                'Result': "You've not uploaded a public key, start your MQTT subscriber!",
                'Reason': 'No public key.'
            }
            return Response(json.dumps(response), 401, content_type='application/json')
        return f(*args, **kwargs)
    return wrapper


@bp_user.get('/check_incoming_chats')
@cross_origin()
@login_required
@authorize_public_key
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
@authorize_public_key
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
@authorize_public_key
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


@bp_user.get('/user-home-page')
@login_required
@authorize_public_key
def user_get():
    users = User.query.all()
    from app import db
    current_user.signed_in = 1

    db.session.commit()
    return render_template("user_home_page.html", users_data=users)


@bp_user.get('/signout')
@login_required
@authorize_public_key
def sign_out():
    from app import db
    current_user.signed_in = 0

    db.session.commit()
    logout_user()
    return redirect(url_for('bp_open.index'))


@bp_user.get('/profile/<user_id>')
@login_required
@authorize_public_key
def get_user_profile(user_id):
    user_id = int(user_id)
    user = get_user_by_id(user_id)
    chat_request = get_user_chat_requests(user_id)
    return render_template('user_profile.html', user=user, chat_requests=chat_request)


@bp_user.post('/message')
@login_required
@authorize_public_key
def message_post():
    data = request.json
    title = data['title']
    body = data['body']
    encrypted_aes_key = data['aes_key']
    receiver_id = data['user_id']
    create_message(title, body, receiver_id, encrypted_aes_key)
    return redirect(url_for('bp_user.user_get'))


@bp_user.get('/messages')
@login_required
@authorize_public_key
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
@authorize_public_key
def mailbox_get():
    messages = get_user_messages()
    return render_template('mailbox.html', messages=messages)


@bp_user.post('/chat_request')
@login_required
@authorize_public_key
def send_chat_request():
    receiver_id = request.form['user_id']
    user = current_user.id
    chat = create_chat_request(user, receiver_id)
    flash(f'Chat accepted. Start your socket server. Connect to chat id: {chat.id}, chat partner id: {chat.receiver_id}')
    return redirect(url_for('bp_user.get_user_profile', user_id=user))
    # return Response(json.dumps(f'Chat accepted. Start your socket client. Connect to chat id: {chat.id}, chat partner '
    #                            f'id: {chat.receiver_id}'), 200, content_type='application/json')


@bp_user.post('/chat_request/accept/<chat_id>')
@login_required
@authorize_public_key
def accept_chat(chat_id):
    accept_chat_request(chat_id)
    user = current_user.id
    chat = Chat.query.filter_by(id=chat_id).first()
    flash(f'Chat accepted. Start your socket client. Connect to chat id: {chat_id}, chat partner id: {chat.sender_id}')
    return redirect(url_for('bp_user.get_user_profile', user_id=user))


@bp_user.get('/admin')
@login_required
@authorize_admin
@authorize_public_key
def get_admin_all_messages():
    messages = get_all_messages()
    return render_template('admin.html', messages=messages)


@bp_user.get('/user_pubkey/<user_id>')
@login_required
@authorize_public_key
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