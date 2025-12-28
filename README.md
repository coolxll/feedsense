# FeedSense

[![Tests](https://github.com/coolxll/feedsense/actions/workflows/tests.yml/badge.svg)](https://github.com/coolxll/feedsense/actions/workflows/tests.yml)
[![Lint](https://github.com/coolxll/feedsense/actions/workflows/lint.yml/badge.svg)](https://github.com/coolxll/feedsense/actions/workflows/lint.yml)
[![codecov](https://codecov.io/gh/coolxll/feedsense/branch/main/graph/badge.svg)](https://codecov.io/gh/coolxll/feedsense)

An AI-powered intelligent RSS reader that uses **Qwen (通义千问)** to automatically analyze and filter articles worth reading.

[中文文档](README_zh.md)

## ✨ Features

- 🤖 **AI Smart Scoring**: Automatically evaluate article quality (0-10 score) using Qwen LLM
- 📊 **Smart Categorization**: Automatically identify article categories (AI, Programming, News, etc.)
- 🎯 **Content Filtering**: Auto-filter marketing fluff and low-quality content
- 💡 **Chinese Analysis**: AI-generated reasons and categories in Chinese
- 🚀 **Fast & Efficient**: Uses qwen-turbo model for speed and cost-effectiveness
- 📝 **Clean CLI**: Simple command-line interface built with Typer

## 🛠️ Tech Stack

- **Python 3.10+**
- **Qwen (通义千问)** - Alibaba Cloud DashScope API
- **Feedparser** - RSS parsing
- **SQLite** - Local data storage
- **Rich** - Beautiful terminal output
- **Typer** - CLI framework

## 📦 Installation

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd rss_auto_read
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
.\venv\Scripts\Activate.ps1

# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API Key

Copy `.env.example` to `.env` and fill in your API key:

```bash
copy .env.example .env  # Windows
# or
cp .env.example .env    # Linux/Mac
```

Edit the `.env` file:

```ini
DASHSCOPE_API_KEY=sk-your-api-key-here
LLM_MODEL_NAME=qwen-turbo
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

> 💡 Get API Key: Visit [Alibaba Cloud DashScope Console](https://dashscope.console.aliyun.com/apiKey)

### 5. Initialize Database

```bash
python manage.py init
```

## 🚀 Usage Guide

### Add RSS Feeds

```bash
python manage.py add http://www.36kr.com/feed
python manage.py add https://www.solidot.org/index.rss
```

### List Subscriptions

```bash
python manage.py list-feeds
```

### Fetch Latest Articles

```bash
python manage.py fetch
```

### AI Analysis

```bash
# Analyze 10 articles (default)
python manage.py analyze

# Specify number of articles
python manage.py analyze --limit 20
```

### View Analysis Report

```bash
# View all analyzed articles
python manage.py report

# Show only high-score articles (≥7)
python manage.py report --score-min 7

# Show top 10 articles
python manage.py report --top 10
```

## 📁 Project Structure

```
rss_auto_read/
├── app/                    # Core application code
│   ├── services/          # Service modules
│   │   ├── rss.py        # RSS fetching service
│   │   └── llm.py        # LLM analysis service
│   ├── config.py         # Configuration management
│   ├── db.py             # Database operations
│   └── cli.py            # CLI command definitions
├── manage.py              # Entry point script
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variable template
└── README.md             # Project documentation
```

## 🎯 Scoring Criteria

The AI scores articles based on the following criteria:

- **0-3**: Marketing content, duplicate news, irrelevant
- **4-6**: General news, interesting but not critical
- **7-8**: Quality tutorials, major releases, insightful opinions
- **9-10**: Groundbreaking news, deep technical analysis, must-read content

## 🔧 Advanced Configuration

### Change Model

Modify `LLM_MODEL_NAME` in `.env`:

```ini
# Speed priority (recommended)
LLM_MODEL_NAME=qwen-turbo

# Balanced performance
LLM_MODEL_NAME=qwen-plus

# Quality priority
LLM_MODEL_NAME=qwen-max
```

### Customize Interest Preferences

Edit the `system_prompt` in `app/services/llm.py` to modify user interest descriptions:

```python
self.system_prompt = """
你是一个智能助手，帮助用户筛选 RSS 订阅内容。
用户对 [your interest areas] 感兴趣。
...
"""
```

## 📝 Example Workflow

```bash
# 1. Add feed
python manage.py add http://www.36kr.com/feed

# 2. Fetch articles
python manage.py fetch

# 3. AI analysis
python manage.py analyze --limit 10

# 4. View high-quality articles
python manage.py report --score-min 7
```

## 🧪 Testing

### Run Tests

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_rss_service.py -v
```

### Test Coverage

The project includes unit tests for:
- ✅ Configuration management
- ✅ Database operations
- ✅ RSS feed fetching and parsing
- ✅ LLM service integration

Current coverage: ~60%

## 🤝 Contributing

Issues and Pull Requests are welcome!

## 📄 License

MIT License

## 🙏 Acknowledgments

- [Qwen (通义千问)](https://tongyi.aliyun.com/) - Powerful AI capabilities
- [Feedparser](https://github.com/kurtmckee/feedparser) - RSS parsing library
- [Rich](https://github.com/Textualize/rich) - Beautiful terminal output
