from StudentConnect import db, login_manager
from datetime import datetime, timezone
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(20), nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    school = db.Column(db.String(100), nullable=False)
    primary_language = db.Column(db.String(20), nullable=False)
    other_languages = db.Column(db.Text, nullable=True)
    country = db.Column(db.String(20), nullable=False)
    course = db.Column(db.String(20), nullable=False)
    profile_picture = db.Column(db.String(250), nullable=False, default='default.jpg')
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy=True)
    received_messages = db.relationship('Message', foreign_keys='Message.receiver_id', backref='receiver', lazy=True)

    mobile_number = db.Column(db.String(15), nullable=True, unique=True)
    whatsapp_number = db.Column(db.String(15), nullable=True, unique=True)
    instagram_handle = db.Column(db.String(50), nullable=True, unique=True)
    linkedin_handle = db.Column(db.String(50), nullable=True, unique=True)
    bio = db.Column(db.Text, nullable=True)  # Bio field
    interests = db.Column(db.Text, nullable=True) 

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)



    def profile_image_url(self):
        return f"/static/images/profile_pics/{self.profile_picture}"

    def __repr__(self):
        return f"User(id={self.id}, username='{self.username}', email='{self.email}', school='{self.school}', primary_language='{self.primary_language}')"


# Define the Message model
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    room = db.Column(db.String(100), nullable=True)  # Optional
    message_content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self):
        return (f"Message(id={self.id}, sender_id={self.sender_id}, receiver_id={self.receiver_id}, "
                f"message_content='{self.message_content[:20]}...', timestamp={self.timestamp})")

