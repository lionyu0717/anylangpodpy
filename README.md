# AnyLangPodPy - AI-Powered Podcast Generation Backend

[简体中文](./README.zh-CN.md) | English

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Backend workflow for [FluentTide](https://www.fluentide.com) - An intelligent language learning application based on Krashen's "i+1" theory that generates personalized podcasts from real-time news.

## 🎯 Overview

AnyLangPodPy is a sophisticated backend system that automatically:
- 🔍 **Crawls** keyword-related news from multiple sources (GDELT, web scraping)
- 🤖 **Generates** podcast scripts using Large Language Models (Deepseek API)
- 🎙️ **Synthesizes** audio podcasts from scripts using Text-to-Speech (Google Cloud TTS)

### Based on Krashen's i+1 Theory

The system intelligently adjusts content difficulty to match learners' proficiency levels, providing comprehensible input that's just beyond their current level - the optimal zone for language acquisition.

## 🏗️ Architecture

```
┌─────────────────┐
│  Keyword Input  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  Phase 1: News Collection               │
│  - GDELT Event Database                 │
│  - Web Scraping (Jina Crawler)          │
│  - Content Aggregation                  │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  Phase 2: Script Generation             │
│  - Content Analysis & Summarization     │
│  - LLM-powered Script Writing           │
│  - Difficulty Adjustment (i+1)          │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  Phase 3: Audio Synthesis               │
│  - Google Cloud Text-to-Speech          │
│  - Multi-language Support               │
│  - Natural Voice Generation             │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│  Podcast Output │
└─────────────────┘
```

## ✨ Features

- 🌐 **Multi-source News Aggregation**: GDELT events + web scraping
- 🧠 **AI-Powered Content Generation**: Deepseek LLM for intelligent script writing
- 🗣️ **High-Quality TTS**: Google Cloud Text-to-Speech with natural voices
- 🌍 **Multi-language Support**: English, Spanish, Chinese, and more
- 📊 **RESTful API**: FastAPI-based endpoints for easy integration
- 🐳 **Docker Ready**: Containerized deployment with docker-compose
- ⚡ **Async Processing**: Background task processing for better performance
- 🔒 **Environment-based Config**: Secure API key management

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Docker & Docker Compose (optional)
- API Keys:
  - Deepseek API Key
  - Google Cloud API Key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/lionyu0717/anylangpodpy.git
   cd anylangpodpy
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

   Required environment variables:
   ```env
   DEEPSEEK_API_KEY=your_deepseek_api_key
   GOOGLE_CLOUD_API_KEY=your_google_cloud_api_key
   JINA_CRAWLER_BASE_URL=http://localhost:3000/
   MAX_URLS_TO_SCRAPE=10
   OUTPUT_DIR=output
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

   Or with Docker:
   ```bash
   docker-compose up -d
   ```

The API will be available at `http://localhost:8088` (or `http://localhost:5050` with Docker).

## 📡 API Endpoints

### Generate Podcast

```http
POST /api/podcast/generate
Content-Type: application/json

{
  "keyword": "climate change",
  "language_code": "en-GB",
  "max_length": 500,
  "use_llm_fallback": true
}
```

**Response:**
```json
{
  "keyword": "climate change",
  "content": "",
  "audio_url": null,
  "status": "processing",
  "request_id": "climate_change_20250116_120000"
}
```

### Check Status

```http
GET /api/podcast/status/{request_id}
```

**Response:**
```json
{
  "keyword": "climate change",
  "content": "Welcome to today's podcast...",
  "audio_url": "/output/climate_change_20250116_120000.mp3",
  "duration": 180.5,
  "status": "success",
  "request_id": "climate_change_20250116_120000",
  "error": null
}
```

## 🛠️ Project Structure

```
anylangpodpy/
├── app/
│   ├── routers/           # API route handlers
│   │   └── podcast.py     # Podcast generation endpoints
│   └── services/          # Core business logic
│       ├── gdelt.py       # GDELT news service
│       ├── scraper.py     # Web scraping service
│       ├── text/
│       │   └── text_generator.py  # LLM text generation
│       ├── tts/
│       │   └── google_tts.py      # Google TTS integration
│       └── podcast_generator.py   # Main orchestration
├── utils/                 # Utility functions
├── tests/                 # Test files
├── config.py             # Configuration management
├── main.py               # Application entry point
├── requirements.txt      # Python dependencies
├── Dockerfile           # Docker configuration
└── docker-compose.yml   # Docker Compose setup
```

## 🔧 Configuration

### Supported Languages

- English (en-GB, en-US)
- Spanish (es-ES, es-US)
- Chinese (zh-CN, zh-TW)
- And more... (See Google Cloud TTS documentation)

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEEPSEEK_API_KEY` | Deepseek API key for LLM | Required |
| `GOOGLE_CLOUD_API_KEY` | Google Cloud API key | Required |
| `JINA_CRAWLER_BASE_URL` | Jina crawler service URL | `http://localhost:3000/` |
| `GDELT_VERSION` | GDELT API version | `2` |
| `MAX_URLS_TO_SCRAPE` | Maximum URLs to scrape | `10` |
| `OUTPUT_DIR` | Output directory for files | `output` |

## 🧪 Testing

```bash
# Run tests
python -m pytest tests/

# Test API manually
python test_api.py
```

## 📝 Command Line Tools

Generate podcast script only:
```bash
python generate_podcast.py "your topic here"
```

Generate audio from script:
```bash
python generate_podcast_audio.py script.txt --language en-GB --voice en-GB-Neural2-A
```

Complete workflow:
```bash
python generate_podcast_complete.py "your topic here" --language en-GB
```

## 🌟 Use Cases

- **Language Learning**: Generate personalized listening materials
- **News Digests**: Daily news summaries in audio format
- **Educational Content**: Topic-based educational podcasts
- **Accessibility**: Convert text content to audio for visually impaired users

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Related Projects

- [FluentTide](https://www.fluentide.com) - Language learning platform
- Frontend Repository: (Link to frontend repo if available)

## 📧 Contact

- Website: [www.fluentide.com](https://www.fluentide.com)
- GitHub: [@lionyu0717](https://github.com/lionyu0717)

## 🙏 Acknowledgments

- **GDELT Project** - For real-time global news data
- **Deepseek** - For powerful LLM capabilities
- **Google Cloud** - For high-quality Text-to-Speech
- **Jina AI** - For web crawling infrastructure
- **Krashen's i+1 Theory** - For the theoretical foundation

---

Built with ❤️ for language learners worldwide
