# 玄助 - 玄幻小说写作助手

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0%2B-lightgrey)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

基于 AI 的玄幻小说创作辅助系统，集成设定管理与智能写作功能。通过 DeepSeek 实现上下文感知的续写/扩写，采用 Notion 式块编辑提升创作体验。

<!-- ![Demo Screenshot](screenshot.png)  后续补充截图 -->

## 核心功能

### 🧙 设定管理系统
- **多维度设定模板**
  - 修炼体系（修仙/魔法/斗气）预置模板库（待完成）
  - 世界地图的文本化层级描述（待完成）
  - 人物关系树状图生成（待完成）
- **动态设定更新**
  - AI 生成内容自动检测新设定（待完成）
  - 手动/半自动设定同步

### ✍️ 智能创作模块
- **双模式 AI 辅助**
  - **扩写模式**：深化场景描写（环境/动作/对话）
  - **续写模式**：延续剧情发展（冲突/转折/伏笔）
- **上下文感知生成**
  - 自动携带当前章节前 1000 字作为上下文
  - 智能匹配相关设定条目

### 📑 文档管理
- Notion 式块编辑体验
- 章节树状导航系统

## 技术栈

**后端**
- Flask + SQLAlchemy
- DeepSeek API 集成


**数据存储**
- SQLite 轻量级数据库
- JSON 格式设定模板库

## 快速开始

### 环境要求
- Python 3.8+
- DeepSeek API Key
