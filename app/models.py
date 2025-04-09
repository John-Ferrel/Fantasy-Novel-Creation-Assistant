from datetime import datetime
from app import db
from sqlalchemy import JSON
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    projects = db.relationship('Project', backref='author', lazy=True)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    story_synopsis = db.Column(db.Text, default="")  # 故事梗概
    keywords = db.Column(db.JSON, default=list)  # 存储核心关键词 ['修仙','复仇','秘境']
    style_template = db.Column(db.String(20), default='玄幻') # 风格模板：热血/古典/轻松
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # 关联设定和章节
    settings = db.relationship('Setting', backref='project', lazy=True)
    chapters = db.relationship('Chapter', backref='project', lazy=True)

class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(20), nullable=False)  # 体系/背景/人物/事件链
    title = db.Column(db.String(100))  # 可选标题（如「修仙等级体系」）
    content = db.Column(db.Text, nullable=False)  # 自由文本内容
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text)
    order = db.Column(db.Integer)  # 章节顺序
    chapter_summary = db.Column(db.Text)  # 本章摘要（AI生成）
    prev_summary = db.Column(db.Text)  # 前章关联摘要
    key_scenes = db.Column(db.JSON, default=list)  # 关键场景标记
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)