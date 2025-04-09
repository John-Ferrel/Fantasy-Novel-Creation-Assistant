import json
import os

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv

# 环境配置
load_dotenv()

# 初始化全局数据结构
def init_data():
    default_data = {
        "world": {
            "continents": "",
            "races": [],
            "power_system": "修仙"
        },
        "cultivation": {
            "levels": {},
            "elements_matrix": pd.DataFrame()
        },
        "map_data": {
            "terrain": "",
            "resources": [],
            "factions": []
        },
        "characters": [],
        "events": [],
        "novel_content": ""
    }
    
    for key in default_data:
        if key not in st.session_state:
            st.session_state[key] = default_data[key]

# AI生成工具
def ai_generate(context, prompt):
    headers = {"Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY')}"}
    
    try:
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json={
                "model": "deepseek-chat",
                "messages": [{
                    "role": "user",
                    "content": f"基于以下设定：\n{json.dumps(context)}\n\n生成：{prompt}"
                }]
            },
            timeout=30
        )
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        st.error(f"生成失败：{str(e)}")
        return ""

# === 页面模块 ===
def world_page():
    st.header("🌍 世界背景设定")
    
    # 初始化数据结构
    if "world" not in st.session_state:
        st.session_state.world = {
            "continents": pd.DataFrame(
                columns=["大陆名称", "面积（万平方公里）", "地貌特征", "气候类型", 
                        "主要资源", "城市分布", "特殊区域", "历史背景"],
                data=[]  # 明确指定数据类型
            ).astype({
                "面积（万平方公里）": "float64",
                "主要资源": "object",
                "城市分布": "object"
            }),
            "races": pd.DataFrame(
                columns=["种族名称", "平均身高（cm）", "肤色", "发色",
                        "寿命（年）", "社会结构", "文化习俗", "特殊能力", "敌对种族"],
                data=[]
            ).astype({
                "平均身高（cm）": "float64",
                "寿命（年）": "int64",
                "敌对种族": "object"
            }),
            "power_system": "修仙体系"
        }
    
    # ===== 大陆设定 =====
    st.subheader("大陆设定")
    
    continent_col_config = {
        "面积（万平方公里）": st.column_config.NumberColumn(
            format="%.1f",
            required=True
        ),
        "主要资源": st.column_config.TextColumn(
            help="用逗号分隔主要资源（例：灵石, 玄铁）"
        ),
        "城市分布": st.column_config.TextColumn(
            help="用逗号分隔主要城市"
        )
    }
    
    with st.expander("大陆编辑器", expanded=True):
        edited_continents = st.data_editor(
            st.session_state.world["continents"],
            column_config=continent_col_config,
            num_rows="dynamic",
            use_container_width=True,
            key="continent_editor"
        )
        
        if st.button("✅ 保存大陆设定"):
            # 转换文本为列表格式存储
            edited_continents["主要资源"] = edited_continents["主要资源"].str.split(r",\s*")
            edited_continents["城市分布"] = edited_continents["城市分布"].str.split(r",\s*")
            st.session_state.world["continents"] = edited_continents
            st.rerun()
    
    # 展示大陆卡片
    if not st.session_state.world["continents"].empty:
        st.subheader("大陆概览")
        tabs = st.tabs(
            [f"🗺️ {name}" for name in st.session_state.world["continents"]["大陆名称"]]
        )
        
        for tab, (_, row) in zip(tabs, st.session_state.world["continents"].iterrows()):
            with tab:
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.metric("面积", f"{row['面积（万平方公里）']}万km²")
                    st.write(f"**气候**: {row['气候类型']}")
                    st.write(f"**资源**: {row['主要资源']}")
                
                with col2:
                    cols = st.columns(2)
                    cols[0].write(f"**地貌特征**: {row['地貌特征']}")
                    cols[1].write(f"**特殊区域**: {row['特殊区域']}")
                    st.divider()
                    st.markdown(f"**历史背景**\n{row['历史背景']}")
    
    # ===== 种族设定 =====
    st.subheader("种族设定")
    
    race_col_config = {
        "平均身高（cm）": st.column_config.NumberColumn(
            format="%d cm",
            required=True
        ),
        "寿命（年）": st.column_config.NumberColumn(
            format="%d 年",
            required=True
        ),
        "敌对种族": st.column_config.TextColumn(
            help="用逗号分隔敌对种族"
        )
    }
    
    with st.expander("种族编辑器", expanded=True):
        edited_races = st.data_editor(
            st.session_state.world["races"],
            column_config=race_col_config,
            num_rows="dynamic",
            use_container_width=True,
            key="race_editor"
        )
        
        if st.button("✅ 保存种族设定"):
            # 转换文本为列表格式存储
            edited_races["敌对种族"] = edited_races["敌对种族"].str.split(r",\s*")
            st.session_state.world["races"] = edited_races
            st.rerun()
    
    # 展示种族卡片
    if not st.session_state.world["races"].empty:
        st.subheader("种族档案")
        for _, row in st.session_state.world["races"].iterrows():
            with st.expander(f"👥 {row['种族名称']}", expanded=False):
                cols = st.columns([1,2,1])
                
                # 基础信息
                cols[0].metric("平均身高", f"{row['平均身高（cm）']}cm")
                cols[0].write(f"**肤色/发色**: {row['肤色']}/{row['发色']}")
                cols[0].write(f"**寿命**: {row['寿命（年）']}年")
                
                # 社会信息
                cols[1].write(f"**社会结构**: {row['社会结构']}")
                cols[1].write(f"**文化习俗**: {row['文化习俗']}")
                cols[1].write(f"**特殊能力**: {row['特殊能力']}")
                
                # 敌对关系
                if pd.notna(row["敌对种族"]) and row["敌对种族"] != "":
                    cols[2].warning(f"敌对种族: {row['敌对种族']}")

    # ===== 力量体系 =====
    st.subheader("核心力量体系")
    st.session_state.world["power_system"] = st.selectbox(
        "选择世界的基础力量规则",
        options=["修仙体系", "魔法体系", "斗气体系", "异能体系", "混合体系"],
        index=0,
        help="此选择将影响后续修炼体系和战斗系统的生成规则"
    )

def cultivation_page():
    st.header("🔄 修炼体系构建")
    
    with st.expander("境界体系"):
        col1, col2 = st.columns(2)
        with col1:
            new_level = st.text_input("境界名称")
        with col2:
            new_power = st.number_input("战力基准值", min_value=0)
        
        if st.button("添加境界"):
            st.session_state.cultivation["levels"][new_level] = new_power
        
        st.write("当前境界体系：")
        for level, power in st.session_state.cultivation["levels"].items():
            st.write(f"{level}: {power}战力")
    
    with st.expander("能量矩阵"):
        elements = ["金", "木", "水", "火", "土"]
        if st.session_state.cultivation["elements_matrix"].empty:
            st.session_state.cultivation["elements_matrix"] = pd.DataFrame(
                "", index=elements, columns=elements
            )
        
        edited_df = st.data_editor(
            st.session_state.cultivation["elements_matrix"],
            column_config={"_index": "元素"}
        )
        st.session_state.cultivation["elements_matrix"] = edited_df

def map_page():
    st.header("🗺️ 世界地图系统")
    
    tab1, tab2, tab3 = st.tabs(["地理层", "资源层", "势力层"])
    
    with tab1:
        st.session_state.map_data["terrain"] = st.text_area(
            "地形特征描述", 
            value=st.session_state.map_data["terrain"],
            height=200
        )
    
    with tab2:
        new_resource = st.text_input("新增资源")
        if st.button("添加资源"):
            st.session_state.map_data["resources"].append(new_resource)
        st.write("已定义资源：", ", ".join(st.session_state.map_data["resources"]))
    
    with tab3:
        new_faction = st.text_input("新增势力")
        if st.button("添加势力"):
            st.session_state.map_data["factions"].append(new_faction)
        st.write("当前势力：", ", ".join(st.session_state.map_data["factions"]))

def character_page():
    st.header("👥 人物关系管理")
    
    with st.form("新增人物"):
        col1, col2 = st.columns(2)
        name = col1.text_input("姓名*")
        level = col2.selectbox("境界", list(st.session_state.cultivation["levels"].keys()))
        
        faction = st.selectbox(
            "所属势力",
            st.session_state.map_data["factions"]
        )
        relations = st.text_input("关联人物（逗号分隔）")
        bio = st.text_area("人物背景", height=100)
        
        if st.form_submit_button("添加人物") and name:
            st.session_state.characters.append({
                "name": name,
                "level": level,
                "faction": faction,
                "relations": [r.strip() for r in relations.split(",")] if relations else [],
                "bio": bio
            })
    
    st.subheader("关系图谱")
    if st.session_state.characters:
        G = nx.Graph()
        for char in st.session_state.characters:
            G.add_node(char["name"], level=char["level"])
            for rel in char["relations"]:
                G.add_edge(char["name"], rel)
        
        fig, ax = plt.subplots(figsize=(10, 8))
        pos = nx.spring_layout(G)
        nx.draw(G, pos, with_labels=True, ax=ax)
        st.pyplot(fig)
    else:
        st.warning("尚未添加人物")

def event_page():
    st.header("⏳ 事件链编排")
    
    with st.form("新增事件"):
        col1, col2 = st.columns(2)
        name = col1.text_input("事件名称*")
        timeline = col2.number_input("时间节点", min_value=0)
        
        event_type = st.selectbox("事件类型", ["主线", "支线", "隐藏"])
        triggers = st.multiselect("触发条件", [e["name"] for e in st.session_state.events])
        desc = st.text_area("事件描述", height=150)
        
        if st.form_submit_button("保存事件") and name:
            st.session_state.events.append({
                "name": name,
                "timeline": timeline,
                "type": event_type,
                "triggers": triggers,
                "desc": desc
            })
    
    st.subheader("事件时间轴")
    if st.session_state.events:
        events_sorted = sorted(st.session_state.events, key=lambda x: x["timeline"])
        for event in events_sorted:
            with st.expander(f"{event['timeline']} - {event['name']} ({event['type']})"):
                st.write(event["desc"])
                if event["triggers"]:
                    st.caption(f"触发条件：{', '.join(event['triggers'])}")
    else:
        st.info("尚未添加事件")

def novel_page():
    st.header("📚 小说生成")
    
    if st.button("整合生成"):
        context = {
            "world": st.session_state.world,
            "characters": st.session_state.characters,
            "events": st.session_state.events
        }
        st.session_state.novel_content = ai_generate(
            context,
            "请根据以上设定生成小说开篇章节，要求：\n"
            "1. 包含世界观铺垫\n2. 引入主要人物\n3. 设置初始冲突"
        )
    
    if st.session_state.novel_content:
        st.subheader("生成内容")
        st.write(st.session_state.novel_content)
        
        st.download_button(
            label="下载小说",
            data=st.session_state.novel_content.encode('utf-8'),
            file_name="my_novel.md",
            mime="text/markdown"
        )

# 主程序
def main():
    st.set_page_config(page_title="玄幻创作助手", layout="wide")
    init_data()
    
    pages = {
        "世界背景": world_page,
        "修炼体系": cultivation_page,
        "地图系统": map_page,
        "人物关系": character_page,
        "事件链": event_page,
        "小说生成": novel_page
    }
    
    st.sidebar.title("导航菜单")
    selection = st.sidebar.radio("前往", list(pages.keys()))
    pages[selection]()

if __name__ == "__main__":
    main()