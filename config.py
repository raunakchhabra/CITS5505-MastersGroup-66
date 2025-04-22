import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    SELECT_KEY = 'GENERATED_SECURE_KEY'
    SQLALCHEMY_DATABASE_URI = ''
    SQLALCHEMY_TRACK_MODIFICATIONS = False