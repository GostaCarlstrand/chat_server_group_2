import datetime

from app import db

message_recv = db.Table('message_recv',
                        db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                        db.Column('message_id', db.Integer, db.ForeignKey('message.id'), primary_key=True)
                        )


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(100))
    admin = db.Column(db.BOOLEAN, default=False)
    signed_in = db.Column(db.Integer, default=0)
    user_ip = db.Column(db.String(150))
    public_rsa_key = db.Column(db.BLOB, default=None)
    sent_messages = db.relationship('Message', backref='sender', lazy=True)
    recv_messages = db.relationship('Message', secondary=message_recv, lazy='subquery',
                                    backref=db.backref('receivers', lazy=True))

    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(250))
    body = db.Column(db.Text)
    read = db.Column(db.BOOLEAN, default=False)
    sent_time = db.Column(db.DateTime, default=datetime.datetime.now())
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    encrypted_aes_key = db.Column(db.String(250), default=None)


class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user_a_accepted = db.Column(db.Integer, default=0)
    user_b_accepted = db.Column(db.Integer, default=0)
    encrypted_ip = db.Column(db.BLOB, default=None)
