from flask_login import current_user
from controllers.user_controller import get_user_by_id


def create_message(title, body, receiver_id):
    from models import Message, User
    user = current_user
    message = Message(title=title, body=body, sender_id=user.id)
    recipient = User.query.filter_by(id=receiver_id).first()
    if not recipient.signed_in:
        from controllers.mqtt_controller import connect_mqtt
        mqtt_publisher = connect_mqtt(current_user.id)
        mqtt_publisher.loop_start()
        mqtt_publisher.publish(f'{receiver_id}', f"You've received a message from {user.name}")
        mqtt_publisher.loop_stop()

    receiver_id = int(receiver_id)
    receiver = get_user_by_id(receiver_id)
    message.receivers.append(receiver)
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