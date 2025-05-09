from flask import Flask
from config import Config
from app.extensions import db, migrate, login_manager

# 蓝图导入在 create_app 内部完成，避免循环导入

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    with app.app_context():
        from app.models import User  # 放在 app_context 内避免提前加载

        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))

        # 注册蓝图
        from app.routes.main import main_bp
        from app.routes.auth import auth_bp
        from app.routes.data import data_bp

        app.register_blueprint(main_bp)
        app.register_blueprint(auth_bp)
        app.register_blueprint(data_bp)

        # （可选）直接创建表，通常用 migrate 管理
        # db.create_all()

    return app
