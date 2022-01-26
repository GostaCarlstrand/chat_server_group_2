from flask_login import current_user
from controllers.user_controller import get_user_by_id


def create_chat_request(user_id, receiver_id):
    from models import Chat
    chat_request = Chat(receiver_id=receiver_id, sender_id=user_id,
                        user_a_accepted=1, user_b_accepted=0)
    from app import db
    db.session.add(chat_request)
    db.session.commit()


def get_user_chat_requests(user_id):
    from models import Chat
    chat_request = Chat.query.filter_by(receiver_id=user_id).first()
    return chat_request






