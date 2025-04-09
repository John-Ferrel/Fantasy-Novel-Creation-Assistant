from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # 确保实例目录存在
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # 加载所有环境变量
    app.config.from_prefixed_env()  # 确保这行在其他配置之前
    
    # 补充DeepSeek配置
    app.config['DEEPSEEK_KEY'] = os.environ.get('DEEPSEEK_KEY')
    app.config['DEEPSEEK_URL'] = os.environ.get('DEEPSEEK_URL')

    # 加载配置
    app.config.from_prefixed_env()
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    with app.app_context():
        db.create_all()
    return app