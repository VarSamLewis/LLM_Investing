import requests
import pandas as pd

def fetch_stock_data(url: str) -> pd.DataFrame:
    r = requests.get(url)
    data = r.json()
    df = pd.DataFrame(data['Time Series (Daily)']).T
    return df

def display_df(df: pd.DataFrame) -> None:
    print(df.head())
    print(f"DataFrame shape (rows, columns): {df.shape}")
    print(f"Total number of elements: {df.size}")
    print(f"Number of rows: {len(df)}")
    print(f"Number of columns: {len(df.columns)}")