from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

conversation_participants = db.Table(
    'conversation_participants',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('conversation_id', db.Integer, db.ForeignKey('conversation.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    profile_picture = db.Column(db.String(128))
    bio = db.Column(db.String(255))
    conversations = db.relationship('Conversation', secondary=conversation_participants, backref=db.backref('participants', lazy='dynamic'))
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy='dynamic')
    received_messages = db.relationship('Message', foreign_keys='Message.recipient_id', backref='recipient', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % self.username

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    messages = db.relationship('Message', backref='conversation', lazy='dynamic')

    def __repr__(self):
        return '<Conversation %r>' % self.id

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    content = db.Column(db.String(1024))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'))
    is_read = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<Message %r>' % self.id
