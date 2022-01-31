import json

import flask
from flask import Flask, Response, Blueprint, request
from controllers import chat_controller
from models import User

bp_api = Blueprint('bp_api', __name__)


@bp_api.get('/<chat_id>')
def get_public_key(chat_id):
    from models import Chat
    chat = Chat.query.filter_by(id=chat_id).first()
    return Response(chat.pub_key, 200, content_type='application/data')


@bp_api.get('/<chat_id>/ip')
def get_encrypted_ip(chat_id):
    from models import Chat
    chat = Chat.query.filter_by(id=chat_id).first()
    encrypted_ip = chat.encrypted_ip
    from app import db
    db.session.delete(chat)
    db.session.commit()
    return Response(encrypted_ip, 200, content_type='application/data')


@bp_api.post('/<chat_id>/ip')
def post_encrypted_ip(chat_id):
    encrypted_ip = flask.request.data
    from models import Chat
    chat = Chat.query.filter_by(id=chat_id).first()
    chat.encrypted_ip = encrypted_ip
    from app import db
    db.session.commit()
    return Response(json.dumps('The encrypted IP-address has been received and will be sent.'), 200, content_type='application/json')


@bp_api.post('/<chat_id>')
def post_public_key(chat_id):
    user_public_key = flask.request.data
    from models import Chat
    chat = Chat.query.filter_by(id=chat_id).first()
    chat.pub_key = user_public_key
    from app import db
    db.session.commit()
    return Response(json.dumps('The key has been received and will be sent.'), 200, content_type='application/json')