# FeedSense

基于 AI 的智能 RSS 阅读器，使用 **通义千问 (Qwen)** 自动分析和筛选值得阅读的文章。

## ✨ 特性

- 🤖 **AI 智能评分**：使用 Qwen 大模型自动评估文章质量（0-10 分）
- 📊 **智能分类**：自动识别文章类别（AI、编程、新闻等）
- 🎯 **内容过滤**：自动过滤营销软文和低质量内容
- 💡 **中文分析**：AI 生成的理由和分类均为中文
- 🚀 **快速高效**：使用 qwen-turbo 模型，速度快、成本低
- 📝 **简洁 CLI**：基于 Typer 的命令行界面，操作简单

## 🛠️ 技术栈

- **Python 3.10+**
- **Qwen (通义千问)** - 阿里云 DashScope API
- **Feedparser** - RSS 解析
- **SQLite** - 本地数据存储
- **Rich** - 美化命令行输出
- **Typer** - CLI 框架

## 📦 安装

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd rss_auto_read
```

### 2. 创建虚拟环境

```bash
python -m venv venv

# Windows
.\venv\Scripts\Activate.ps1

# Linux/Mac
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置 API Key

复制 `.env.example` 为 `.env`，并填入你的 API Key：

```bash
copy .env.example .env  # Windows
# 或
cp .env.example .env    # Linux/Mac
```

编辑 `.env` 文件：

```ini
DASHSCOPE_API_KEY=sk-your-api-key-here
LLM_MODEL_NAME=qwen-turbo
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

> 💡 获取 API Key：访问 [阿里云 DashScope 控制台](https://dashscope.console.aliyun.com/apiKey)

### 5. 初始化数据库

```bash
python manage.py init
```

## 🚀 使用指南

### 添加 RSS 订阅源

```bash
python manage.py add http://www.36kr.com/feed
python manage.py add https://www.solidot.org/index.rss
```

### 查看订阅列表

```bash
python manage.py list-feeds
```

### 抓取最新文章

```bash
python manage.py fetch
```

### AI 分析文章

```bash
# 分析 10 篇文章（默认）
python manage.py analyze

# 指定分析数量
python manage.py analyze --limit 20
```

### 查看分析报告

```bash
# 查看所有已分析的文章
python manage.py report

# 只看高分文章（≥7分）
python manage.py report --score-min 7

# 查看前 10 篇
python manage.py report --top 10
```

## 📁 项目结构

```
rss_auto_read/
├── app/                    # 核心应用代码
│   ├── services/          # 服务模块
│   │   ├── rss.py        # RSS 抓取服务
│   │   └── llm.py        # LLM 分析服务
│   ├── config.py         # 配置管理
│   ├── db.py             # 数据库操作
│   └── cli.py            # CLI 命令定义
├── manage.py              # 入口脚本
├── requirements.txt       # Python 依赖
├── .env.example          # 环境变量模板
└── README.md             # 项目文档
```

## 🎯 评分标准

AI 会根据以下标准对文章进行评分：

- **0-3 分**：营销内容、重复新闻、不相关内容
- **4-6 分**：一般新闻，有趣但不重要
- **7-8 分**：优质教程、重大发布、有见地的观点
- **9-10 分**：突破性新闻、深度技术分析、必读内容

## 🔧 高级配置

### 更换模型

在 `.env` 中修改 `LLM_MODEL_NAME`：

```ini
# 速度优先（推荐）
LLM_MODEL_NAME=qwen-turbo

# 平衡性能
LLM_MODEL_NAME=qwen-plus

# 质量优先
LLM_MODEL_NAME=qwen-max
```

### 自定义兴趣偏好

编辑 `app/services/llm.py` 中的 `system_prompt`，修改用户兴趣描述：

```python
self.system_prompt = """
你是一个智能助手，帮助用户筛选 RSS 订阅内容。
用户对 [你的兴趣领域] 感兴趣。
...
"""
```

## 📝 示例工作流

```bash
# 1. 添加订阅源
python manage.py add http://www.36kr.com/feed

# 2. 抓取文章
python manage.py fetch

# 3. AI 分析
python manage.py analyze --limit 10

# 4. 查看高质量文章
python manage.py report --score-min 7
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

- [Qwen (通义千问)](https://tongyi.aliyun.com/) - 提供强大的 AI 能力
- [Feedparser](https://github.com/kurtmckee/feedparser) - RSS 解析库
- [Rich](https://github.com/Textualize/rich) - 美化终端输出
