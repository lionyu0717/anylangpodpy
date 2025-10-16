# AnyLangPodPy - AI 驱动的播客生成后端

简体中文 | [English](./README.md)

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[FluentTide](https://www.fluentide.com) 的后端工作流 - 基于克拉申"i+1"理论，实时获取新闻并生成个性化播客的智能语言学习应用。

## 🎯 项目概述

AnyLangPodPy 是一个复杂的后端系统，能够自动完成：
- 🔍 **爬取**关键词相关的新闻（GDELT 事件数据库、网页抓取）
- 🤖 **生成**播客脚本（使用大语言模型 Deepseek API）
- 🎙️ **合成**音频播客（使用文本转语音技术 Google Cloud TTS）

### 基于克拉申的 i+1 理论

系统智能调整内容难度以匹配学习者的水平，提供略高于当前水平的可理解输入 - 这是语言习得的最佳区域。

## 🏗️ 系统架构

```
┌─────────────────┐
│   关键词输入    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  阶段 1: 新闻收集                       │
│  - GDELT 事件数据库                     │
│  - 网页爬取（Jina Crawler）             │
│  - 内容聚合                             │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  阶段 2: 脚本生成                       │
│  - 内容分析与总结                       │
│  - LLM 驱动的脚本撰写                   │
│  - 难度调整（i+1）                      │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  阶段 3: 音频合成                       │
│  - Google Cloud 文本转语音              │
│  - 多语言支持                           │
│  - 自然语音生成                         │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│   播客输出      │
└─────────────────┘
```

## ✨ 核心特性

- 🌐 **多源新闻聚合**：GDELT 事件 + 网页爬取
- 🧠 **AI 内容生成**：Deepseek 大语言模型智能撰写脚本
- 🗣️ **高质量 TTS**：Google Cloud 文本转语音，自然人声
- 🌍 **多语言支持**：英语、西班牙语、中文等
- 📊 **RESTful API**：基于 FastAPI 的接口，易于集成
- 🐳 **Docker 就绪**：使用 docker-compose 容器化部署
- ⚡ **异步处理**：后台任务处理，提升性能
- 🔒 **环境配置**：安全的 API 密钥管理

## 🚀 快速开始

### 前置要求

- Python 3.9+
- Docker & Docker Compose（可选）
- API 密钥：
  - Deepseek API Key
  - Google Cloud API Key

### 安装步骤

1. **克隆仓库**
   ```bash
   git clone https://github.com/lionyu0717/anylangpodpy.git
   cd anylangpodpy
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **配置环境变量**
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，填入你的 API 密钥
   ```

   必需的环境变量：
   ```env
   DEEPSEEK_API_KEY=你的_deepseek_api_密钥
   GOOGLE_CLOUD_API_KEY=你的_google_cloud_api_密钥
   JINA_CRAWLER_BASE_URL=http://localhost:3000/
   MAX_URLS_TO_SCRAPE=10
   OUTPUT_DIR=output
   ```

4. **运行应用**
   ```bash
   python main.py
   ```

   或使用 Docker：
   ```bash
   docker-compose up -d
   ```

API 将在 `http://localhost:8088` 可用（使用 Docker 时为 `http://localhost:5050`）。

## 📡 API 接口

### 生成播客

```http
POST /api/podcast/generate
Content-Type: application/json

{
  "keyword": "气候变化",
  "language_code": "zh-CN",
  "max_length": 500,
  "use_llm_fallback": true
}
```

**响应：**
```json
{
  "keyword": "气候变化",
  "content": "",
  "audio_url": null,
  "status": "processing",
  "request_id": "气候变化_20250116_120000"
}
```

### 查询状态

```http
GET /api/podcast/status/{request_id}
```

**响应：**
```json
{
  "keyword": "气候变化",
  "content": "欢迎收听今天的播客...",
  "audio_url": "/output/气候变化_20250116_120000.mp3",
  "duration": 180.5,
  "status": "success",
  "request_id": "气候变化_20250116_120000",
  "error": null
}
```

## 🛠️ 项目结构

```
anylangpodpy/
├── app/
│   ├── routers/           # API 路由处理器
│   │   └── podcast.py     # 播客生成端点
│   └── services/          # 核心业务逻辑
│       ├── gdelt.py       # GDELT 新闻服务
│       ├── scraper.py     # 网页爬取服务
│       ├── text/
│       │   └── text_generator.py  # LLM 文本生成
│       ├── tts/
│       │   └── google_tts.py      # Google TTS 集成
│       └── podcast_generator.py   # 主编排器
├── utils/                 # 工具函数
├── tests/                 # 测试文件
├── config.py             # 配置管理
├── main.py               # 应用入口
├── requirements.txt      # Python 依赖
├── Dockerfile           # Docker 配置
└── docker-compose.yml   # Docker Compose 设置
```

## 🔧 配置说明

### 支持的语言

- 英语（en-GB, en-US）
- 西班牙语（es-ES, es-US）
- 中文（zh-CN, zh-TW）
- 更多语言...（参见 Google Cloud TTS 文档）

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `DEEPSEEK_API_KEY` | Deepseek API 密钥 | 必需 |
| `GOOGLE_CLOUD_API_KEY` | Google Cloud API 密钥 | 必需 |
| `JINA_CRAWLER_BASE_URL` | Jina 爬虫服务 URL | `http://localhost:3000/` |
| `GDELT_VERSION` | GDELT API 版本 | `2` |
| `MAX_URLS_TO_SCRAPE` | 最大爬取 URL 数 | `10` |
| `OUTPUT_DIR` | 输出文件目录 | `output` |

## 🧪 测试

```bash
# 运行测试
python -m pytest tests/

# 手动测试 API
python test_api.py
```

## 📝 命令行工具

仅生成播客脚本：
```bash
python generate_podcast.py "你的话题"
```

从脚本生成音频：
```bash
python generate_podcast_audio.py script.txt --language zh-CN --voice zh-CN-Neural2-A
```

完整工作流：
```bash
python generate_podcast_complete.py "你的话题" --language zh-CN
```

## 🌟 应用场景

- **语言学习**：生成个性化的听力材料
- **新闻摘要**：每日新闻音频摘要
- **教育内容**：基于主题的教育播客
- **无障碍访问**：为视障用户将文本内容转换为音频

## 🤝 贡献指南

欢迎贡献！请随时提交 Pull Request。

1. Fork 本仓库
2. 创建您的特性分支（`git checkout -b feature/AmazingFeature`）
3. 提交您的更改（`git commit -m 'Add some AmazingFeature'`）
4. 推送到分支（`git push origin feature/AmazingFeature`）
5. 打开一个 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🔗 相关项目

- [FluentTide](https://www.fluentide.com) - 语言学习平台
- 前端仓库：（如有前端仓库链接请添加）

## 📧 联系方式

- 网站：[www.fluentide.com](https://www.fluentide.com)
- GitHub：[@lionyu0717](https://github.com/lionyu0717)

## 🙏 致谢

- **GDELT Project** - 提供实时全球新闻数据
- **Deepseek** - 提供强大的大语言模型能力
- **Google Cloud** - 提供高质量的文本转语音服务
- **Jina AI** - 提供网页爬取基础设施
- **克拉申的 i+1 理论** - 提供理论基础

---

用 ❤️ 为全球语言学习者打造

