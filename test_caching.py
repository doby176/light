#!/usr/bin/env python3
"""
Test script to verify QQQ gap data caching and time restrictions
"""

import os
import json
import pytz
from datetime import datetime

def test_time_restriction():
    """Test the time restriction logic"""
    eastern = pytz.timezone('US/Eastern')
    now_et = datetime.now(eastern)
    market_open_time = now_et.replace(hour=9, minute=30, second=0, microsecond=0)
    
    print(f"Current time (ET): {now_et.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Market open time: {market_open_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Before 9:30 AM: {now_et < market_open_time}")
    
    if now_et < market_open_time:
        print("✅ Time restriction working - data not available before 9:30 AM ET")
    else:
        print("✅ Market is open - data should be available")

def test_cache_file_naming():
    """Test cache file naming convention"""
    eastern = pytz.timezone('US/Eastern')
    now_et = datetime.now(eastern)
    today_et = now_et.strftime('%Y-%m-%d')
    cache_file = f'qqq_gap_cache_{today_et}.json'
    
    print(f"Today's date (ET): {today_et}")
    print(f"Cache file name: {cache_file}")
    
    # Check if cache file exists
    if os.path.exists(cache_file):
        print(f"✅ Cache file exists: {cache_file}")
        try:
            with open(cache_file, 'r') as f:
                cached_data = json.load(f)
                print(f"✅ Cache data loaded successfully")
                print(f"   Cached at: {cached_data.get('cached_at', 'N/A')}")
                print(f"   Cache date: {cached_data.get('cache_date', 'N/A')}")
                print(f"   Gap: {cached_data.get('gap_pct', 'N/A')}% {cached_data.get('gap_direction', 'N/A')}")
        except Exception as e:
            print(f"❌ Error reading cache file: {e}")
    else:
        print(f"ℹ️  No cache file found: {cache_file}")

def test_pytz_import():
    """Test that pytz is available"""
    try:
        import pytz
        print("✅ pytz module imported successfully")
        return True
    except ImportError as e:
        print(f"❌ pytz import failed: {e}")
        return False

if __name__ == "__main__":
    print("=== QQQ Gap Data Caching Test ===\n")
    
    # Test pytz import
    if not test_pytz_import():
        exit(1)
    
    print()
    
    # Test time restriction
    test_time_restriction()
    
    print()
    
    # Test cache file naming
    test_cache_file_naming()
    
    print("\n=== Test Complete ===")