from flask import Flask
from app.routes.courses import courses_bp

def create_app():
    app = Flask(__name__)
    app.register_blueprint(courses_bp)
    return app
