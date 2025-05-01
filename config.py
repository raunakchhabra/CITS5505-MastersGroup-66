# config.py
import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Existing configuration
    SECRET_KEY = 'your-secret-key'  # to be replaced with a secure key
    DATABASE = os.path.join(os.getcwd(), 'users.db')  # SQLite route
    MAIL_SERVER = 'smtp.gmail.com'  # Mail server (only simulated here)
    MAIL_PORT = 587
    MAIL_USERNAME = 'your-email@gmail.com'  # replace with new email
    MAIL_PASSWORD = 'your-email-password'  # replace with new email password
    
    # New configuration for SQLAlchemy and file uploads
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(basedir, 'app', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
