#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import re

def scrape_qqq_data():
    """Scrape QQQ data from CNBC website"""
    try:
        url = "https://www.cnbc.com/quotes/QQQ"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        print(f"Fetching data from: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        print("Successfully fetched the page")
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the Summary section with Key Stats
        summary_section = soup.find('div', class_='Summary-subsection')
        if not summary_section:
            print("Could not find Summary-subsection")
            return None
        
        print("Found Summary-subsection")
        
        # Look for the Key Stats title
        key_stats_title = summary_section.find('h3', class_='Summary-title', string=lambda text: text and 'KEY STATS' in text.upper())
        if not key_stats_title:
            print("Could not find Key Stats title")
            return None
        
        print("Found Key Stats title")
        
        # Find the stats list
        stats_list = summary_section.find('ul', class_='Summary-data')
        if not stats_list:
            print("Could not find Summary-data list")
            return None
        
        print("Found Summary-data list")
        
        # Extract the data
        data = {}
        stats_items = stats_list.find_all('li', class_='Summary-stat')
        
        print(f"Found {len(stats_items)} stat items")
        
        for item in stats_items:
            label_elem = item.find('span', class_='Summary-label')
            value_elem = item.find('span', class_='Summary-value')
            
            if label_elem and value_elem:
                label = label_elem.get_text(strip=True)
                value = value_elem.get_text(strip=True)
                
                print(f"Found: {label} = {value}")
                
                if label in ['Open', 'Prev Close']:
                    data[label] = value
        
        # Calculate gap percentage if we have both Open and Prev Close
        if 'Open' in data and 'Prev Close' in data:
            try:
                open_price = float(data['Open'])
                prev_close = float(data['Prev Close'])
                gap_percentage = ((open_price - prev_close) / prev_close) * 100
                data['Gap %'] = f"{gap_percentage:.2f}%"
                print(f"Calculated gap: {data['Gap %']}")
            except (ValueError, ZeroDivisionError):
                data['Gap %'] = "N/A"
                print("Could not calculate gap percentage")
        
        return data
        
    except Exception as e:
        print(f"Error scraping QQQ data: {str(e)}")
        return None

if __name__ == "__main__":
    print("Testing QQQ data scraping...")
    data = scrape_qqq_data()
    
    if data:
        print("\nSuccessfully scraped QQQ data:")
        for key, value in data.items():
            print(f"  {key}: {value}")
    else:
        print("Failed to scrape QQQ data")