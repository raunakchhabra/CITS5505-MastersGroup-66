from flask import Flask
from flask_login import login_required, current_user
from flask_socketio import SocketIO
from config import Config, TestConfig

# Initialize extensions
from app.extensions import db, migrate, login_manager

# Initialize SocketIO outside of create_app
socketio = SocketIO()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Override with TestConfig if TESTING flag is passed
    if app.config.get("TESTING"):
        app.config.from_object(TestConfig)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    socketio.init_app(app)

    with app.app_context():
        # Import models
        from app.models import User, Data, SharedData, DataType, SharedPermission

        # User loader for Flask-Login
        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))

        # Register blueprints - import them here to avoid circular imports
        from app.routes.main import main_bp
        from app.routes.auth import auth_bp
        from app.routes.data import data_bp
        from app.routes.exercise import exercise_bp
        from app.routes.api import api_bp

        app.register_blueprint(main_bp)
        app.register_blueprint(auth_bp)
        app.register_blueprint(data_bp)
        app.register_blueprint(exercise_bp)
        app.register_blueprint(api_bp)

        # Shell context for flask shell
        @app.shell_context_processor
        def make_shell_context():
            return {
                'db': db,
                'User': User,
                'Data': Data,
                'SharedData': SharedData,
                'DataType': DataType,
                'SharedPermission': SharedPermission,
                'socketio': socketio
            }

    return app