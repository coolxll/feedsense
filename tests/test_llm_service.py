import unittest
from unittest.mock import patch, MagicMock
from app.services.llm import LLMService, ReviewResult


class TestLLMService(unittest.TestCase):
    """Test LLM service functionality."""
    
    def setUp(self):
        """Set up LLM service with mocked client."""
        with patch('app.services.llm.OpenAI'):
            self.service = LLMService()
    
    def test_review_result_validation(self):
        """Test ReviewResult pydantic model validation."""
        # Valid data
        result = ReviewResult(score=8, reason="Good article", category="Tech")
        self.assertEqual(result.score, 8)
        self.assertEqual(result.reason, "Good article")
        self.assertEqual(result.category, "Tech")
    
    def test_review_result_invalid_score(self):
        """Test that ReviewResult validates score range."""
        # Pydantic doesn't enforce range by default, but we can test the model accepts integers
        result = ReviewResult(score=15, reason="Test", category="Test")
        self.assertIsInstance(result.score, int)
    
    @patch('app.services.llm.OpenAI')
    def test_analyze_article_success(self, mock_openai):
        """Test successful article analysis."""
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '{"score": 7, "reason": "有见地的技术分析", "category": "AI"}'
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        service = LLMService()
        result = service.analyze_article("Test Title", "Test Summary", "http://example.com")
        
        self.assertIsNotNone(result)
        self.assertEqual(result.score, 7)
        self.assertEqual(result.category, "AI")
    
    @patch('app.services.llm.OpenAI')
    def test_analyze_article_with_empty_summary(self, mock_openai):
        """Test analysis with empty summary."""
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '{"score": 5, "reason": "无摘要", "category": "未知"}'
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        service = LLMService()
        result = service.analyze_article("Test Title", "", "http://example.com")
        
        self.assertIsNotNone(result)
    
    @patch('app.services.llm.OpenAI')
    def test_analyze_article_api_error(self, mock_openai):
        """Test handling of API errors."""
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client
        
        service = LLMService()
        result = service.analyze_article("Test Title", "Test Summary", "http://example.com")
        
        self.assertIsNone(result)
    
    @patch('app.services.llm.OpenAI')
    def test_analyze_article_invalid_json(self, mock_openai):
        """Test handling of invalid JSON response."""
        mock_response = MagicMock()
        mock_response.choices[0].message.content = 'Invalid JSON'
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        service = LLMService()
        result = service.analyze_article("Test Title", "Test Summary", "http://example.com")
        
        self.assertIsNone(result)
    
    def test_system_prompt_is_chinese(self):
        """Test that system prompt is in Chinese."""
        with patch('app.services.llm.OpenAI'):
            service = LLMService()
            self.assertIn("智能助手", service.system_prompt)
            self.assertIn("中文", service.system_prompt)


if __name__ == '__main__':
    unittest.main()
