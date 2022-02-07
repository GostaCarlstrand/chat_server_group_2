import fnmatch
import json
import os
from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, Response, request
from flask_login import logout_user, login_required, current_user

from controllers.chat_controller import create_chat_request, get_user_chat_requests, accept_chat_request
from controllers.message_controller import get_user_messages, create_message, get_all_messages
from controllers.user_controller import get_user_by_id
from models import User, Chat
import PIL.Image as Image
import io
import base64

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
                'Result': "You've not uploaded a public key Start your MQTT subscriber!",
                'Reason': 'No public key.'
            }
            return Response(json.dumps(response), 401, content_type='application/json')
        return f(*args, **kwargs)
    return wrapper


@bp_user.get('/check_incoming_chats')
@login_required
# temp removed @authorize_public_key
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
@login_required
# temp removed @authorize_public_key
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
@login_required
# temp removed @authorize_public_key
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
# temp removed @authorize_public_key
def user_get():
    users = User.query.all()
    from app import db
    current_user.signed_in = 1

    db.session.commit()
    return render_template("user_home_page.html", users_data=users)


@bp_user.get('/signout')
@login_required
# temp removed @authorize_public_key
def sign_out():
    from app import db
    current_user.signed_in = 0

    db.session.commit()
    logout_user()
    return redirect(url_for('bp_open.index'))


@bp_user.get('/profile/<user_id>')
@login_required
# temp removed @authorize_public_key
def get_user_profile(user_id):
    user_id = int(user_id)
    user = get_user_by_id(user_id)
    chat_request = get_user_chat_requests(user_id)
    return render_template('user_profile.html', user=user, chat_requests=chat_request)


@bp_user.post('/message')
@login_required
# temp removed @authorize_public_key
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
# temp removed @authorize_public_key
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
# temp removed @authorize_public_key
def mailbox_get():
    messages = get_user_messages()
    return render_template('mailbox.html', messages=messages)


@bp_user.post('/chat_request')
@login_required
# temp removed @authorize_public_key
def send_chat_request():
    receiver_id = request.form['user_id']
    user = current_user.id
    create_message('Chat request sent', 'Your request has been sent. Wait for a message with further instructions.'
                   , current_user.id)
    create_chat_request(user, receiver_id)
    return redirect(url_for('bp_user.mailbox_get'))


@bp_user.post('/chat_request/accept/<chat_id>')
@login_required
# temp removed @authorize_public_key
def accept_chat(chat_id):
    accept_chat_request(chat_id)
    create_message('Chat accepted', 'Start your client server.', current_user.id)
    chat = Chat.query.filter_by(id=chat_id).first()
    create_message(f'Chat accepted by {current_user.name}', 'Start your socket server.', chat.sender_id)
    return redirect(url_for('bp_user.mailbox_get'))


@bp_user.get('/admin')
@login_required
@authorize_admin
# temp removed @authorize_public_key
def get_admin_all_messages():
    messages = get_all_messages()
    return render_template('admin.html', messages=messages)


@bp_user.get('/user_pubkey/<user_id>')
@login_required
# temp removed @authorize_public_key
def get_user_public_key(user_id):
    user = get_user_by_id(user_id)
    public_key = user.public_rsa_key.decode("utf-8")
    return Response(json.dumps(public_key), 200, content_type='application/json')


@bp_user.get('/profile-picture/<user_id>')
@login_required
def get_user_profile_picture(user_id):
    #path = os.path.abspath(f"./static/users/{current_user.id}.txt")

    def find(pattern, path):
        result = []
        for root, dirs, files in os.walk(path):
            for name in files:
                if fnmatch.fnmatch(name, pattern):
                    result.append(os.path.join(root, name))
        return result

    my_file = find('*.jpeg', f"/Users/gosta/PycharmProjects/chat_server_group_2/static/users/{user_id}")
    if my_file:
        my_file = my_file[0].split('chat_server_group_2')
        path = my_file[1]
        return Response(json.dumps(path), 200, content_type='application/json')
    else:
        path = "/static/users/19/hidethepainharold.jpeg"        # Default profile picture
        return Response(json.dumps(path), 200, content_type='application/json')


@bp_user.post('/change_image')
def changeProfilePicture():
    data = request
    picture_binary = data.data
    picture_str = picture_binary.decode('utf-8')
    picture_split_str = picture_str.split('"data:image/jpeg;base64,')
    picture_binary = picture_split_str[1].encode()

    b = base64.b64decode(picture_binary)

    img = Image.open(io.BytesIO(b))

    def find(pattern, path):
        result = []
        for root, dirs, files in os.walk(path):
            for name in files:
                if fnmatch.fnmatch(name, pattern):
                    result.append(os.path.join(root, name))
        return result

    user_path = f"/Users/gosta/PycharmProjects/chat_server_group_2/static/users/{current_user.id}"
    user_path += '/profile-picture.jpeg'
    my_file = find('*.jpeg', user_path)

    if my_file:
        os.remove(my_file[0])
        img.save(user_path, 'JPEG')
    else:
        img.save(user_path, 'JPEG')

    return Response({'status': 'profile_picture_uploaded'}, 200, content_type='application/json');
