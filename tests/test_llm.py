import unittest
from unittest.mock import patch, Mock
import os
from src.llm import LLM


class TestLLM(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_prompt = "Test prompt for stock analysis"
        
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test_api_key'})
    @patch('src.llm.anthropic.Anthropic')
    def test_llm_initialization(self, mock_anthropic):
        """Test LLM class initialization."""
        # Arrange
        mock_client = Mock()
        mock_anthropic.return_value = mock_client
        
        # Act
        llm = LLM()
        
        # Assert
        self.assertEqual(llm.client, mock_client)
        self.assertIn("stock data", llm.system_prompt)
        self.assertEqual(llm.max_tokens, 5000)
        mock_anthropic.assert_called_once_with(api_key='test_api_key')

    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test_api_key'})
    @patch('src.llm.anthropic.Anthropic')
    def test_generate_response_success(self, mock_anthropic):
        """Test successful response generation."""
        # Arrange
        mock_client = Mock()
        mock_response = Mock()
        mock_response.content = [Mock(text="Buy QQQ at $480")]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client
        
        llm = LLM()
        
        # Act
        result = llm.generate_response(self.test_prompt)
        
        # Assert
        self.assertEqual(result, "Buy QQQ at $480")
        mock_client.messages.create.assert_called_once()
        
        # Verify the parameters passed to create
        call_args = mock_client.messages.create.call_args[1]
        self.assertEqual(call_args['model'], 'claude-3-5-haiku-latest')
        self.assertEqual(call_args['max_tokens'], 5000)
        self.assertEqual(call_args['messages'][0]['content'], self.test_prompt)

    def test_llm_initialization_no_api_key(self):
        """Test LLM initialization without API key."""
        with patch.dict(os.environ, {'ANTHROPIC_API_KEY': ''}, clear=False):
            if 'PATH' not in os.environ:
                with patch.dict(os.environ, {'PATH': ''}):
                    with self.assertRaises((ValueError, TypeError)) as context:
                        LLM()
            else:
                with self.assertRaises((ValueError, TypeError)) as context:
                    LLM()
            
            error_msg = str(context.exception).lower()
            self.assertTrue(
                any(word in error_msg for word in ['api', 'key', 'token', 'auth']),
                f"Expected API key related error, got: {context.exception}"
            )

    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test_api_key'})
    @patch('src.llm.anthropic.Anthropic')
    def test_generate_response_api_error(self, mock_anthropic):
        """Test handling of API errors during response generation."""
        # Arrange
        mock_client = Mock()
        mock_client.messages.create.side_effect = Exception("API Error")
        mock_anthropic.return_value = mock_client
        
        llm = LLM()
        
        # Act & Assert
        with self.assertRaises(Exception):
            llm.generate_response(self.test_prompt)


if __name__ == '__main__':
    unittest.main()