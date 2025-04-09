from datetime import datetime
from app import db

# 用户表（暂不实现登录，留作扩展）
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    projects = db.relationship('Project', backref='author', lazy=True)

# 项目表（一个用户可创建多个项目）
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    settings = db.relationship('Setting', backref='project', uselist=False)
    chapters = db.relationship('Chapter', backref='project', lazy=True)

# 设定表（与项目一对一关联）
class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    cultivation_system = db.Column(db.Text)  # 修炼体系
    world_background = db.Column(db.Text)    # 世界背景
    characters = db.Column(db.Text)          # 人物关系（Markdown文本）
    events = db.Column(db.Text)              # 事件链（Markdown文本）

# 章节表
class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    content = db.Column(db.Text)             # Markdown内容
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    order = db.Column(db.Integer)            # 章节顺序