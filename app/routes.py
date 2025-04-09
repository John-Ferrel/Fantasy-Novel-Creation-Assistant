from flask import Blueprint, render_template, request, jsonify
from app.models import Project, Setting, Chapter, db
from datetime import datetime
import json
import requests
from flask import current_app

main_bp = Blueprint('main', __name__)

# ================== 通用路由 ==================
@main_bp.route('/')
def index():
    """首页：显示所有项目"""
    projects = Project.query.order_by(Project.created_at.desc()).all()
    return render_template('index.html', projects=projects)

# ================== 项目路由 ==================
@main_bp.route('/project', methods=['POST'])
def create_project():
    """创建新项目"""
    data = request.json
    new_project = Project(
        title=data['title'],
        created_at=datetime.utcnow(),
        user_id=1  # 暂用测试用户
    )
    db.session.add(new_project)
    db.session.commit()
    return jsonify({"id": new_project.id})

@main_bp.route('/project/<int:project_id>')
def project_detail(project_id):
    """项目详情页（小说创作入口）"""
    project = Project.query.get_or_404(project_id)
    chapters = Chapter.query.filter_by(project_id=project_id).order_by(Chapter.order).all()
    return render_template('novel.html', project=project, chapters=chapters)

# ================== 章节路由 ==================
@main_bp.route('/chapter/<int:chapter_id>', methods=['GET', 'POST'])
def handle_chapter(chapter_id):
    """章节内容处理"""
    chapter = Chapter.query.get_or_404(chapter_id)
    
    if request.method == 'POST':
        # 保存章节内容
        chapter.content = json.dumps(request.json['content'])
        db.session.commit()
        return jsonify({"status": "saved"})
    
    # 获取章节内容
    return jsonify({
        "id": chapter.id,
        "title": chapter.title,
        "content": json.loads(chapter.content) if chapter.content else []
    })

# ================== 设定路由 ==================
@main_bp.route('/setting/<int:project_id>')
def setting_page(project_id):
    """设定页面渲染"""
    project = Project.query.get_or_404(project_id)
    settings = Setting.query.filter_by(project_id=project_id).all()
    return render_template('setting.html',  # 确保模板存在
                         project=project,
                         settings=settings)

# ================== AI生成路由 ==================

def build_prompt(project_id, chapter_id, current_text, action):
    # 获取上下文数据
    project = Project.query.get(project_id)
    chapter = Chapter.query.get(chapter_id)
    prev_chapters = Chapter.query.filter(
    Chapter.project_id == project_id,
    Chapter.order.isnot(None),  # 新增非空检查
    Chapter.order < chapter.order
).order_by(Chapter.order.desc()).limit(3).all() if chapter.order else []

    # 构建分层提示
    prompt = f"""
        # 角色指令
        你是一名专业玄幻小说{action}助手，正在创作作品《{project.title}》
        当前章节：{chapter.title}（第{chapter.order}章）
        作品风格：{project.style_template}

        # 故事总纲
        {project.story_synopsis}

        # 前情提要（最近3章）
        {''.join([f'第{c.order}章摘要：{c.chapter_summary}' for c in prev_chapters])}

        # 本章上下文
        前文摘要：{chapter.prev_summary}
        关键场景：{', '.join(chapter.key_scenes if chapter.key_scenes else [])}
        核心关键词：{', '.join(project.keywords)}

        # 当前段落
        {current_text}

        # 创作要求
        1. 严格遵循世界观设定
        2. 保持每段在800-1000字之间
        3. 使用Markdown格式标注重点
        4. 包含至少1个伏笔设定

        请进行{action}创作：
        """
    return prompt

def post_process(text, keywords, settings):
    # 替换矛盾词汇
    setting_keywords = {s.category: s.content for s in settings}
    for kw in setting_keywords:
        if "现代" in setting_keywords[kw] and "手机" in text:
            text = text.replace("手机", "传音玉简")
    
    # 强制包含关键词
    for keyword in keywords:
        if keyword not in text:
            text += f"\n（涉及{keyword}相关内容）"
    
    return text

@main_bp.route('/generate', methods=['POST'])
def ai_generate():
    data = request.json
    
    # 获取上下文
    project = Project.query.get(data['project_id'])
    settings = Setting.query.filter_by(project_id=data['project_id']).all()
    
    # 构建智能提示
    prompt = build_prompt(
        project_id=data['project_id'],
        chapter_id=data['chapter_id'],
        current_text=data['current_text'],
        action=data['action']
    )
    # print(prompt)  

    # API参数动态调整
    params = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7 if data['action'] == "续写" else 0.8,
        "top_p": 0.9,
        "max_tokens": 500,
        "presence_penalty": 0.5
    }

        # 使用本地anythingllm api 测试
    try:
        headers ={"accept": "application/json",
                 "Content-Type": "application/json", 
                 "Authorization": "Bearer GMHM9V4-GZJM737-NYRK3KS-77K9TNK"}
        data = {
        "mode": "chat",
        "message":prompt,
            }
        
        # 发送 POST 请求
        response = requests.post('http://localhost:3001/api/v1/workspace/novel-test/chat', headers=headers, json=data)

        # 检查响应状态码
        if response.status_code == 200:  # 200 表示成功
            result = response.json()
            result = result['textResponse'].split('</think>')[-1].strip()  
            print("生成成功：", result)
            return jsonify({"generated_text": result})
        else:
            print(f"生成失败，状态码：{response.status_code}，错误信息：{response.text}")
    except requests.RequestException as e:
        print(f"请求发生错误：{e}")

        # 调用API
    # try:
        # headers = {"Authorization": f"Bearer {current_app.config['DEEPSEEK_KEY']}"}
        # response = requests.post(current_app.config['DEEPSEEK_URL'] , json=params, headers=headers)
        # result = response.json()

        # 后处理
    #     generated_text = post_process(
    #         result['choices'][0]['message']['content'],
    #         project.keywords,
    #         [s.content for s in settings]
    #     )

    #     return jsonify({"generated_text": generated_text})

    # except requests.exceptions.RequestException as e:
    #     current_app.logger.error(f"API连接失败：{str(e)}")
    #     return jsonify({"error": "AI服务暂时不可用"}), 503
    # except KeyError as e:
    #     current_app.logger.error(f"响应解析失败：{str(e)}")
    #     return jsonify({"error": "AI响应格式异常"}), 500

# 获取所有章节
@main_bp.route('/chapters/<int:project_id>')
def get_chapters(project_id):
    chapters = Chapter.query.filter_by(project_id=project_id).order_by(Chapter.order).all()
    return jsonify([{
        "id": c.id,
        "title": c.title,
        "order": c.order
    } for c in chapters])

# 创建新章节（补充完整）
@main_bp.route('/chapter', methods=['POST'])
def create_chapter():
    data = request.json
    new_chapter = Chapter(
        title=data['title'],
        content=json.dumps(["新章节内容"]),
        project_id=data['project_id'],
        order=data.get('order', 0),
        key_scenes=[]  # 确保初始化空列表
    )
    db.session.add(new_chapter)
    db.session.commit()
    return jsonify({"id": new_chapter.id})