import unittest
from unittest.mock import patch, Mock
import pandas as pd
import requests
from src.data_pull import fetch_stock_data, display_df
import io
import sys


class TestDataPull(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures with sample stock data."""
        self.sample_api_response = {
            'Time Series (Daily)': {
                '2025-09-22': {
                    '1. open': '480.00',
                    '2. high': '485.00',
                    '3. low': '478.00',
                    '4. close': '482.50',
                    '5. volume': '1000000'
                },
                '2025-09-21': {
                    '1. open': '475.00',
                    '2. high': '481.00',
                    '3. low': '474.00',
                    '4. close': '479.75',
                    '5. volume': '1200000'
                }
            }
        }
        
        self.test_url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=QQQ&outputsize=compact&apikey=test'

    @patch('src.data_pull.requests.get')
    def test_fetch_stock_data_success(self, mock_get):
        """Test successful stock data fetch."""
        # Arrange
        mock_response = Mock()
        mock_response.json.return_value = self.sample_api_response
        mock_get.return_value = mock_response
        
        # Act
        result = fetch_stock_data(self.test_url)
        
        # Assert
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        self.assertEqual(len(result.columns), 5)
        mock_get.assert_called_once_with(self.test_url)
        
    @patch('src.data_pull.requests.get')
    def test_fetch_stock_data_api_error(self, mock_get):
        """Test handling of API errors."""
        # Arrange
        mock_get.side_effect = requests.exceptions.RequestException("API Error")
        
        # Act & Assert
        with self.assertRaises(requests.exceptions.RequestException):
            fetch_stock_data(self.test_url)
            
    @patch('src.data_pull.requests.get')
    def test_fetch_stock_data_invalid_json(self, mock_get):
        """Test handling of invalid JSON response."""
        # Arrange
        mock_response = Mock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response
        
        # Act & Assert
        with self.assertRaises(ValueError):
            fetch_stock_data(self.test_url)

    def test_display_df(self):
        """Test DataFrame display function."""
        # Arrange
        test_df = pd.DataFrame({
            'A': [1, 2, 3],
            'B': [4, 5, 6],
            'C': [7, 8, 9]
        })
        
        # Capture stdout
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        # Act
        display_df(test_df)
        
        # Reset stdout
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()
        
        # Assert
        self.assertIn("DataFrame shape (rows, columns): (3, 3)", output)
        self.assertIn("Total number of elements: 9", output)
        self.assertIn("Number of rows: 3", output)
        self.assertIn("Number of columns: 3", output)


if __name__ == '__main__':
    unittest.main()