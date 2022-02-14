from flask_login import current_user
from controllers.user_controller import get_user_by_id


def create_message(title, body, receiver_id, encrypted_aes_key):
    from models import Message, User
    user = current_user
    message = Message(title=title, body=body, sender_id=user.id, encrypted_aes_key=encrypted_aes_key)
    recipient = get_user_by_id(int(receiver_id))

    if not recipient.signed_in:
        from controllers.mqtt_controller import connect_mqtt
        mqtt_publisher = connect_mqtt(current_user.id)
        mqtt_publisher.loop_start()
        mqtt_publisher.loop_stop()
        mqtt_publisher.publish(f'{receiver_id}', f"You've received a message from {user.name}")

    message.receivers.append(recipient)
    from app import db
    db.session.add(message)
    db.session.commit()


def get_user_messages():
    from app import db
    for message in current_user.recv_messages:
        message.read = True
    db.session.commit()
    return current_user.recv_messages


def get_all_messages():
    from models import Message
    message = Message.query.all()
    return message


def create_server_message(title, body, recv_id):
    from models import ServerMessage
    message = ServerMessage(title=title, body=body, recv_id=recv_id)
    from app import db
    db.session.add(message)
    db.session.commit()


def msg_from_server(user_id):
    from models import ServerMessage
    messages = ServerMessage.query.filter_by(recv_id=user_id).all()
    return messages

