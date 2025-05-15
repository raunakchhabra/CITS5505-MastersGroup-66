# config.py
import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Existing configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key')  # to be replaced with a secure key
    DATABASE = os.path.join(os.getcwd(), os.environ.get('DATABASE_PATH', 'users.db'))  # SQLite route
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')  # Mail server (only simulated here)
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'your-email@gmail.com')  # replace with new email
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'your-email-password')  # replace with new email password

    # New configuration for SQLAlchemy and file uploads
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI',
                                             'sqlite:///' + os.path.join(basedir, 'app.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get('SQLALCHEMY_TRACK_MODIFICATIONS', 'False').lower() == 'true'
    UPLOAD_FOLDER = os.path.join(basedir, os.environ.get('UPLOAD_FOLDER', 'app/uploads'))
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB max upload