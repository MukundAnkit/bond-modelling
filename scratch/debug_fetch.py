"""Debug script for FRED data fetching."""

import datetime

import pandas_datareader.data as web

start_date = datetime.date(2023, 1, 1)
end_date = datetime.date(2023, 1, 31)

series_ids = {
    "DGS1MO": 1 / 12,
    "DGS3MO": 0.25,
    "DGS6MO": 0.5,
    "DGS1": 1.0,
    "DGS2": 2.0,
    "DGS3": 3.0,
    "DGS5": 5.0,
    "DGS7": 7.0,
    "DGS10": 10.0,
    "DGS20": 20.0,
    "DGS30": 30.0,
}

try:
    df = web.DataReader(list(series_ids.keys()), "fred", start_date, end_date)
    print(df.head())
    print("Success!")
except Exception as e:
    print(f"Failed: {e}")
