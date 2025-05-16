#__init__.py
from flask import Flask
from flask_login import LoginManager  # Corrected import
from flask_socketio import SocketIO
from config import Config
from app.extensions import db, migrate

# Initialize extensions outside of create_app
db = db
migrate = migrate
login_manager = LoginManager()  # Corrected initialization
socketio = SocketIO()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with the app
    db.init_app(app)
    migrate.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    socketio.init_app(app)

    # Import blueprints and models *within* create_app, *after* db is initialized
    from app.models import User, Data, SharedData, DataType, SharedPermission  # Import models here
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.data import data_bp
    from app.routes.exercise import exercise_bp
    from app.routes.api import api_bp

    with app.app_context():

        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))

        app.register_blueprint(main_bp)
        app.register_blueprint(auth_bp)
        app.register_blueprint(data_bp)
        app.register_blueprint(exercise_bp)
        app.register_blueprint(api_bp)

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
