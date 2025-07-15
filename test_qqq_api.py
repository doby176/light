#!/usr/bin/env python3

import requests
import json

def test_qqq_api():
    api_key = "9K03GJJCB96AJCO3"
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=QQQ&apikey={api_key}"
    
    print(f"Testing API URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        print(f"Response status: {response.status_code}")
        print(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
        
        if "Error Message" in data:
            print(f"Error: {data['Error Message']}")
        elif "Note" in data:
            print(f"Note: {data['Note']}")
        elif "Time Series (Daily)" in data:
            time_series = data["Time Series (Daily)"]
            dates = sorted(time_series.keys(), reverse=True)
            print(f"Available dates: {dates[:5]}")  # Show first 5 dates
            if len(dates) >= 2:
                yesterday = dates[0]
                day_before = dates[1]
                yesterday_close = float(time_series[yesterday]["4. close"])
                day_before_close = float(time_series[day_before]["4. close"])
                gap_percentage = ((yesterday_close - day_before_close) / day_before_close) * 100
                print(f"Yesterday close: ${yesterday_close}")
                print(f"Day before close: ${day_before_close}")
                print(f"Gap percentage: {gap_percentage:.2f}%")
            else:
                print("Insufficient data for gap calculation")
        else:
            print(f"Unexpected response: {data}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_qqq_api()