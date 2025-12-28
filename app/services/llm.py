import json
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import Optional
from app.config import config
from app.db import get_db


class ReviewResult(BaseModel):
    score: int = Field(
        description="A score from 0 to 10 indicating how worth reading this article is."
    )
    reason: str = Field(
        description="A brief explanation (1-2 sentences) of why this score was given."
    )
    category: str = Field(
        description="The general topic/category of the article (e.g. AI, Programming, News, Gadgets)."
    )


class LLMService:
    def __init__(self):
        self.client = OpenAI(api_key=config.API_KEY, base_url=config.BASE_URL)
        self.system_prompt = """
        你是一个智能助手，帮助用户筛选 RSS 订阅内容。
        用户对高质量的技术内容、AI 发展、重要科技新闻和深度教程感兴趣。
        
        分析提供的文章元数据（标题、摘要）。
        你必须忽略营销软文、泛泛的新闻稿和低价值内容。
        
        以有效的 JSON 格式返回你的分析，格式如下：
        {
            "score": <0-10>,
            "reason": "<简短理由，用中文>",
            "category": "<分类，用中文>"
        }
        
        评分指南：
        - 0-3: 营销内容、重复新闻、不相关。
        - 4-6: 一般新闻，有趣但不重要。
        - 7-8: 优质教程、重大发布、有见地的观点。
        - 9-10: 突破性新闻、深度技术分析、必读内容。
        
        请用中文输出 reason 和 category 字段。
        """

    def analyze_article(
        self, title: str, summary: str, link: str
    ) -> Optional[ReviewResult]:
        content_preview = summary[:1000] if summary else "No summary provided."

        user_prompt = f"""
        Article Title: {title}
        Link: {link}
        Content Snippet: {content_preview}
        
        Analyze this article.
        """

        try:
            response = self.client.chat.completions.create(
                model=config.MODEL_NAME,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content
            data = json.loads(content)
            return ReviewResult(**data)

        except Exception as e:
            # Fallback or error logging
            print(f"Error analyzing article '{title}': {e}")
            return None

    def process_pending(self, limit=10):
        """Analyzes pending 'new' articles."""
        with get_db() as conn:
            # Fetch articles that are 'new'
            cursor = conn.execute(
                "SELECT * FROM articles WHERE status='new' LIMIT ?", (limit,)
            )
            articles = cursor.fetchall()

        analyzed_count = 0
        for article in articles:
            print(f"Analyzing: {article['title']}...")
            result = self.analyze_article(
                article["title"], article["summary"], article["link"]
            )

            if result:
                with get_db() as conn:
                    conn.execute(
                        """
                        UPDATE articles 
                        SET status='analyzed', score=?, analysis=?, category=?
                        WHERE id=?
                    """,
                        (result.score, result.reason, result.category, article["id"]),
                    )
                    conn.commit()
                analyzed_count += 1
            else:
                # Mark as skipped or try again later?
                # For now, mark as skipped to avoid infinite error loops
                with get_db() as conn:
                    conn.execute(
                        "UPDATE articles SET status='error' WHERE id=?",
                        (article["id"],),
                    )
                    conn.commit()

        return analyzed_count
