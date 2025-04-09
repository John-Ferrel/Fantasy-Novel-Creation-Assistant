# main.py
import streamlit as st
import sqlite3
from datetime import datetime

# 自定义CSS样式
st.markdown("""
<style>
/* 主容器样式 */
.stTextInput>div>div>input {
    border-radius: 8px;
    padding: 12px;
    font-size: 16px;
}

/* 文本块容器 */
.text-block {
    border: 1px solid #e0e0e0;
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 20px;
    background: #f8f9fa;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* 按钮样式 */
.stButton>button {
    border-radius: 6px;
    padding: 8px 16px;
    margin: 4px 0;
}

/* 字符统计 */
.char-counter {
    color: #666;
    font-size: 0.85em;
    margin-top: 4px;
}
</style>
""", unsafe_allow_html=True)

# 初始化数据库
conn = sqlite3.connect('novel.db')
c = conn.cursor()

# 创建章节表
c.execute('''CREATE TABLE IF NOT EXISTS chapters
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
             title TEXT,
             content TEXT,
             created_at TIMESTAMP)''')

# 修改设定表结构（更合理的存储方式）
c.execute('''CREATE TABLE IF NOT EXISTS settings
            (id INTEGER PRIMARY KEY,
             book_name TEXT,
             category TEXT,
             content TEXT)''')
conn.commit()

# 初始化session状态
if "current_chapter" not in st.session_state:
    st.session_state.update({
        "current_page": "writing",
        "current_chapter": {
            "title": "",
            "blocks": [{"user_input": "", "ai_output": ""}]
        },
        "current_settings": {
            "reference_book": "不使用参考书籍",
            "cultivation": "",
            "world": "",
            "map": "",
            "characters": "",
            "events": ""
        }
    })

# 预设书籍数据
PRESET_BOOKS = {
    "不使用参考书籍": {},
    "凡人修仙传": {
        "cultivation": "境界划分：\n- 炼气期\n- 筑基期\n- 金丹期\n- 元婴期\n- 化神期",
        "world": "世界体系：\n人界 → 灵界 → 仙界\n主要势力：\n- 天南各派\n- 乱星海妖族\n- 大晋王朝",
        "map": "主要地区：\n1. 天南地区\n2. 乱星海\n3. 大晋王朝",
        "characters": "主要人物：\n- 韩立（主角）\n- 南宫婉（道侣）\n- 大衍神君（导师）",
        "events": "核心事件链：\n1. 七玄门入门\n2. 血色禁地试炼\n3. 虚天殿夺宝"
    },
    "斗破苍穹": {
        "cultivation": "等级体系：\n- 斗之气\n- 斗者\n- 斗师\n- 大斗师\n- 斗灵\n- 斗王",
        "world": "世界设定：\n斗气大陆\n主要势力：\n- 萧家\n- 云岚宗\n- 魂殿",
        "map": "地域分布：\n1. 加玛帝国\n2. 黑角域\n3. 中州",
        "characters": "人物关系：\n- 萧炎（男主）\n- 药尘（师父）\n- 萧薰儿（青梅竹马）",
        "events": "主线事件：\n1. 三年之约\n2. 陨落心炎夺取\n3. 魂殿决战"
    }
}

def render_text_block(block_index):
    """渲染带样式的文本块"""
    with st.container():
        # 使用自定义CSS类
        st.markdown('<div class="text-block">', unsafe_allow_html=True)
        
        # 用户输入区
        user_input = st.text_area(
            "你的创作内容",
            value=st.session_state.current_chapter["blocks"][block_index]["user_input"],
            height=150,
            key=f"user_input_{block_index}",
            label_visibility="collapsed",
            placeholder="在此输入你的创作内容..."
        )
        st.markdown(f'<div class="char-counter">字符数：{len(user_input)}</div>', 
                   unsafe_allow_html=True)
        
        # 操作按钮
        col1, col2, col3 = st.columns([2,2,6])
        with col1:
            if st.button("✨ 扩写", key=f"expand_{block_index}", use_container_width=True):
                generate_ai_content(block_index, "expand")
        with col2:
            if st.button("⏩ 续写", key=f"continue_{block_index}", use_container_width=True):
                generate_ai_content(block_index, "continue")
        
        # AI生成区
        ai_output = st.text_area(
            "AI生成内容",
            value=st.session_state.current_chapter["blocks"][block_index]["ai_output"],
            height=150,
            key=f"ai_output_{block_index}",
            label_visibility="collapsed",
            placeholder="AI生成内容将显示在此处..."
        )
        st.markdown(f'<div class="char-counter">字符数：{len(ai_output)}</div>', 
                   unsafe_allow_html=True)
        
        # 重写按钮
        if st.button("🔄 重新生成", key=f"rewrite_{block_index}", use_container_width=True):
            generate_ai_content(block_index, "rewrite")
        
        st.markdown('</div>', unsafe_allow_html=True)

def render_settings_page():
    st.header("⚙️ 世界观设定")
    
    # 参考书籍选择
    selected_book = st.selectbox(
        "选择参考模板", 
        options=["不使用参考书籍", "凡人修仙传", "斗破苍穹", "其他（手动输入）"],
        index=0,
        key="book_select"
    )
    
    # 处理书籍选择逻辑
    if selected_book == "其他（手动输入）":
        custom_book = st.text_input("📖 请输入参考书籍名称")
        if st.button("✨ AI生成设定"):
            with st.spinner("正在生成基础设定..."):
                # 调用生成函数（需补充API调用）
                generated = generate_book_settings(custom_book)
                st.session_state.current_settings.update(generated)
                st.success("基础设定已生成！")
    elif selected_book != "不使用参考书籍":
        if st.button("🔄 加载预设"):
            st.session_state.current_settings.update(PRESET_BOOKS[selected_book])
            st.session_state.current_settings["reference_book"] = selected_book
            st.success(f"已加载《{selected_book}》预设设定！")
    
    # 设定选项卡
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "修炼体系", "世界背景", "地图", 
        "人物关系", "事件链"
    ])
    
    with tab1:
        st.text_area("修炼体系", 
                    value=st.session_state.current_settings["cultivation"],
                    height=300,
                    key="cultivation_edit")
    
    with tab2:
        st.text_area("世界背景", 
                    value=st.session_state.current_settings["world"],
                    height=300,
                    key="world_edit")
    
    with tab3:
        st.text_area("地图设定", 
                    value=st.session_state.current_settings["map"],
                    height=300,
                    key="map_edit")
    
    with tab4:
        st.text_area("人物关系", 
                    value=st.session_state.current_settings["characters"],
                    height=300,
                    key="characters_edit")
    
    with tab5:
        st.text_area("事件链", 
                    value=st.session_state.current_settings["events"],
                    height=300,
                    key="events_edit")
    
    # 保存按钮
    if st.button("💾 保存当前设定"):
        for category in ["cultivation", "world", "map", "characters", "events"]:
            c.execute('''INSERT OR REPLACE INTO settings 
                        (book_name, category, content)
                        VALUES (?, ?, ?)''',
                     (st.session_state.current_settings["reference_book"],
                      category,
                      st.session_state.current_settings[category]))
        conn.commit()
        st.success("设定已保存！")
    
    if st.button("← 返回创作"):
        st.session_state.current_page = "writing"
        st.rerun()

def generate_book_settings(book_name):
    """调用API生成设定（示例版）"""
    # 实际应调用DeepSeek API，示例返回数据
    return {
        "cultivation": f"《{book_name}》修炼体系：\n- 境界一\n- 境界二\n- 境界三",
        "world": f"《{book_name}》世界背景：\n- 主要大陆\n- 核心势力分布",
        "map": f"《{book_name}》地图：\n- 重要地区1\n- 重要地区2",
        "characters": f"《{book_name}》人物关系：\n- 主角\n- 导师\n- 反派",
        "events": f"《{book_name}》核心事件：\n1. 起始事件\n2. 关键转折\n3. 最终决战"
    }


def generate_ai_content(block_index, mode):
    """模拟AI生成内容"""
    prompt = st.session_state.current_chapter["blocks"][block_index]["user_input"]
    
    # 此处应调用真实API，以下为模拟数据
    sample_outputs = {
        "expand": f"{prompt}\n\n[扩写内容] 这里是对上文详细的场景描写...",
        "continue": f"{prompt}\n\n[续写内容] 随后故事发生了新的转折...",
        "rewrite": f"[优化版本] 这里是对原文的改写版本..."
    }
    
    st.session_state.current_chapter["blocks"][block_index]["ai_output"] = sample_outputs[mode]

def save_chapter():
    """保存章节到数据库"""
    if not st.session_state.current_chapter["title"]:
        st.error("请先输入章节标题！")
        return
    
    content = "\n\n".join([
        f"用户输入：{block['user_input']}\nAI生成：{block['ai_output']}"
        for block in st.session_state.current_chapter["blocks"]
    ])
    
    try:
        c.execute('''
            INSERT INTO chapters (title, content, created_at)
            VALUES (?, ?, ?)
        ''', (
            st.session_state.current_chapter["title"],
            content,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.commit()
        st.success("章节保存成功！")
    except Exception as e:
        st.error(f"保存失败：{str(e)}")

def export_txt():
    """导出为TXT文件"""
    if not st.session_state.current_chapter["title"]:
        st.error("请先输入章节标题！")
        return
    
    content = f"# {st.session_state.current_chapter['title']}\n\n"
    content += "\n\n".join([
        block["ai_output"] for block in st.session_state.current_chapter["blocks"]
    ])
    
    st.download_button(
        label="📥 下载TXT文件",
        data=content,
        file_name=f"{st.session_state.current_chapter['title']}.txt",
        mime="text/plain"
    )

def main():
    # 侧边栏导航
    with st.sidebar:
        if st.button("⚙️ 设定管理", use_container_width=True):
            st.session_state.current_page = "settings"
        
        st.header("📚 历史章节")
        chapters = c.execute("SELECT id, title FROM chapters").fetchall()
        for chap_id, title in chapters:
            if st.button(f"{title} (#{chap_id})"):
                # 待实现的加载功能
                st.info("加载功能待实现")

    # 页面路由
    if st.session_state.current_page == "settings":
        render_settings_page()
    else:
        # 原有创作页面保持不变
        st.title("📖 玄幻小说创作系统")
        
        # 章节标题输入
        st.session_state.current_chapter["title"] = st.text_input(
            "章节标题",
            placeholder="请输入本章标题",
            key="chapter_title"
        )
        
        # 动态生成文本块
        for i in range(len(st.session_state.current_chapter["blocks"])):
            render_text_block(i)
        
        # 添加新块按钮
        if st.button("➕ 添加新的内容块"):
            st.session_state.current_chapter["blocks"].append({
                "user_input": "",
                "ai_output": ""
            })
            st.rerun()
        
        # 底部操作栏
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 保存章节"):
                save_chapter()
        with col2:
            export_txt()



if __name__ == "__main__":
    main()