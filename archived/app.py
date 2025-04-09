from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

# 需在模型定义后导入
from models import *

@app.route('/')
def index():
    return "Novel Helper 首页（后续替换为模板）"

if __name__ == '__main__':
    app.run(debug=True)