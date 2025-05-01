from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'  # Set the login view

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    with app.app_context():
        # Register blueprints
        from app.routes.main import main_bp
        from app.routes.auth import auth_bp
        from app.routes.data import data_bp
        
        app.register_blueprint(main_bp)
        app.register_blueprint(auth_bp)
        app.register_blueprint(data_bp)
        
        # Create database tables
        db.create_all()
        
        return app
