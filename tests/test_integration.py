import unittest
from unittest.mock import patch, Mock
import pandas as pd
import os
from src.data_pull import fetch_stock_data
from src.llm import LLM


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete workflow."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_api_response = {
            'Time Series (Daily)': {
                '2025-09-22': {
                    '1. open': '480.00',
                    '2. high': '485.00',
                    '3. low': '478.00',
                    '4. close': '482.50',
                    '5. volume': '1000000'
                }
            }
        }
        self.test_url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=QQQ&outputsize=compact&apikey=test'

    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test_api_key'})
    @patch('src.llm.anthropic.Anthropic')
    @patch('src.data_pull.requests.get')
    def test_complete_workflow(self, mock_get, mock_anthropic):
        """Test the complete data fetch -> LLM analysis workflow."""
        # Arrange
        # Mock stock data API
        mock_stock_response = Mock()
        mock_stock_response.json.return_value = self.sample_api_response
        mock_get.return_value = mock_stock_response
        
        # Mock LLM
        mock_client = Mock()
        mock_llm_response = Mock()
        mock_llm_response.content = [Mock(text="BUY QQQ at $480. Target: $490. Stop: $475.")]
        mock_client.messages.create.return_value = mock_llm_response
        mock_anthropic.return_value = mock_client
        
        # Act
        df = fetch_stock_data(self.test_url)
        llm = LLM()
        prompt = f"Generate buy sell recommendations for the next 30 days\n{df.to_string()}"
        response = llm.generate_response(prompt)
        
        # Assert
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 1)
        self.assertIn("BUY QQQ", response)
        self.assertIn("480", response)
        
        # Verify API calls were made
        mock_get.assert_called_once_with(self.test_url)
        mock_client.messages.create.assert_called_once()

    @patch('src.data_pull.requests.get')
    def test_data_fetch_error_handling(self, mock_get):
        """Test error handling in data fetch."""
        # Arrange
        mock_get.side_effect = Exception("Network error")
        
        # Act & Assert
        with self.assertRaises(Exception) as context:
            fetch_stock_data(self.test_url)
        
        self.assertIn("Network error", str(context.exception))


if __name__ == '__main__':
    unittest.main()