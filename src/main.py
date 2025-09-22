import requests
import pandas as pd
import os
from data_pull import fetch_stock_data, display_df
from llm import LLM

if __name__ == "__main__":
    ticker = 'QQQ'
    api_key = os.getenv('ALPHAVANTAGE_API')
    period = 'compact'  
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&outputsize={period}&apikey={api_key}'
    try:
        df = fetch_stock_data(url)
        #display_df(df)
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred querying stock data: {http_err}")
        raise
    except Exception as err:
        print(f"Other error occurred: {err}")
        raise
    try:
        llm = LLM()
    except Exception as err:
        print(f"Error initializing LLM: {err}")
        raise

    prompt = f"Generate buy sell recommendations for the next 30 days\n{df.to_string()}"
    try:
        response = llm.generate_response(prompt)
        print(response)
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred prompting models: {http_err}")
        raise
    except Exception as err:
        print(f"Other error occurred: {err}")
        raise

