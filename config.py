# config.py
import os

class Config:
    SECRET_KEY = 'your-secret-key'  #  to be replaced with a secure key
    DATABASE = os.path.join(os.getcwd(), 'users.db')  # SQLite route
    MAIL_SERVER = 'smtp.gmail.com'  # Mail server (only simulated here)
    MAIL_PORT = 587
    MAIL_USERNAME = 'your-email@gmail.com'  # replace with new email
    MAIL_PASSWORD = 'your-email-password'  #replace with new email password