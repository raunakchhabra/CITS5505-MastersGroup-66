from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import enum

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    data = db.relationship('Data', backref='owner', lazy=True)
    received_shares = db.relationship('SharedData', foreign_keys='SharedData.recipient_id',
                                     backref='recipient', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class DataType(enum.Enum):
    VOCABULARY = "vocabulary"
    STUDY_TIME = "study_time" 
    ASSESSMENT = "assessment"
    OTHER = "other"

class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    data_type = db.Column(db.Enum(DataType), nullable=False)
    description = db.Column(db.Text, nullable=True)
    file_path = db.Column(db.String(255), nullable=True)  # For storing file paths
    content = db.Column(db.Text, nullable=True)  # For directly storing content
    metadata = db.Column(db.JSON, nullable=True)  # For storing other metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    shared_data = db.relationship('SharedData', backref='data', lazy=True)
    
    def __repr__(self):
        return f'<Data {self.title}>'

class SharedPermission(enum.Enum):
    READ = "read"
    EDIT = "edit"

class SharedData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_id = db.Column(db.Integer, db.ForeignKey('data.id'), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    permission = db.Column(db.Enum(SharedPermission), default=SharedPermission.READ)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    owner = db.relationship('User', foreign_keys=[owner_id], backref='shared_data')
    
    def __repr__(self):
        return f'<SharedData {self.id}>'
