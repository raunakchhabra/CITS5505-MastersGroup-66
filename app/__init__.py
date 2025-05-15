from flask import Flask
from flask_login import login_required, current_user
from config import Config, TestConfig  # Include TestConfig
from app.extensions import db, migrate, login_manager
from app.models import Data, SharedData, DataType, SharedPermission
from app.routes.api import api_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Override with TestConfig if TESTING flag is passed (optional)
    if app.config.get("TESTING"):
        app.config.from_object(TestConfig)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    with app.app_context():
        from app.models import User

        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))

        # Register blueprints
        from app.routes.main import main_bp
        from app.routes.auth import auth_bp
        from app.routes.data import data_bp
        from app.routes.exercise import exercise_bp

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
                'SharedPermission': SharedPermission
            }

    return app
