import json
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import Optional
from app.config import config
from app.db import get_db

class ReviewResult(BaseModel):
    score: int = Field(description="A score from 0 to 10 indicating how worth reading this article is.")
    reason: str = Field(description="A brief explanation (1-2 sentences) of why this score was given.")
    category: str = Field(description="The general topic/category of the article (e.g. AI, Programming, News, Gadgets).")

class LLMService:
    def __init__(self):
        self.client = OpenAI(
            api_key=config.API_KEY,
            base_url=config.BASE_URL
        )
        self.system_prompt = """
        You are an intelligent assistant helping a user filter RSS feeds.
        The user is interested in high-quality technical content, AI developments, significant tech news, and insightful tutorials.
        
        Analyze the provided article metadata (Title, Summary). 
        You must ignore marketing fluff, generic press releases, and low-value content.
        
        Return your analysis in valid JSON format matching the schema:
        {
            "score": <0-10>,
            "reason": "<short justification>",
            "category": "<category>"
        }
        
        Scoring Guide:
        - 0-3: Marketing, duplicate news, irrelevant.
        - 4-6: General news, interesting but not critical.
        - 7-8: Good tutorial, major release, insightful opinion.
        - 9-10: Groundbreaking news, deep technical dive, must-read.
        """

    def analyze_article(self, title: str, summary: str, link: str) -> Optional[ReviewResult]:
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
                    {'role': 'system', 'content': self.system_prompt},
                    {'role': 'user', 'content': user_prompt}
                ],
                response_format={"type": "json_object"}
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
            cursor = conn.execute("SELECT * FROM articles WHERE status='new' LIMIT ?", (limit,))
            articles = cursor.fetchall()
            
        analyzed_count = 0
        for article in articles:
            print(f"Analyzing: {article['title']}...")
            result = self.analyze_article(article['title'], article['summary'], article['link'])
            
            if result:
                with get_db() as conn:
                    conn.execute('''
                        UPDATE articles 
                        SET status='analyzed', score=?, analysis=?, category=?
                        WHERE id=?
                    ''', (result.score, result.reason, result.category, article['id']))
                    conn.commit()
                analyzed_count += 1
            else:
                # Mark as skipped or try again later?
                # For now, mark as skipped to avoid infinite error loops
                 with get_db() as conn:
                    conn.execute("UPDATE articles SET status='error' WHERE id=?", (article['id'],))
                    conn.commit()
                    
        return analyzed_count
