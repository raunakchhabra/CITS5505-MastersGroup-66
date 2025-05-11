from flask import Flask
from flask_login import LoginManager
from config import Config
from app.extensions import db, migrate, login_manager
from app.models import Data, SharedData, DataType, SharedPermission

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    with app.app_context():
        from app.models import User  

        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))

   
        from app.routes.main import main_bp
        from app.routes.auth import auth_bp
        from app.routes.data import data_bp

        app.register_blueprint(main_bp)
        app.register_blueprint(auth_bp)
        app.register_blueprint(data_bp)

        # db.create_all()

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
