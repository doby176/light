"""
Minimal pandas replacement for Python 3.13 compatibility
"""
import csv
from datetime import datetime, date
import sqlite3
from typing import List, Dict, Any, Optional

class NaT:
    """Not a Time - pandas NaT replacement"""
    pass

def to_datetime(value) -> datetime:
    """Convert value to datetime"""
    if isinstance(value, str):
        return datetime.fromisoformat(value.replace('Z', '+00:00'))
    elif isinstance(value, datetime):
        return value
    elif isinstance(value, date):
        return datetime.combine(value, datetime.min.time())
    else:
        raise ValueError(f"Cannot convert {value} to datetime")

def isna(value) -> bool:
    """Check if value is NaN/NaT"""
    if value is None:
        return True
    if isinstance(value, str) and value.lower() in ['nan', 'nat', '']:
        return True
    return False

class DataFrame:
    """Simple DataFrame replacement"""
    def __init__(self, data=None):
        if data is None:
            self.data = []
        elif isinstance(data, list):
            self.data = data
        else:
            self.data = []
    
    @property
    def shape(self):
        if not self.data:
            return (0, 0)
        return (len(self.data), len(self.data[0]) if self.data else 0)
    
    @property
    def columns(self):
        if not self.data:
            return []
        return list(self.data[0].keys())
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, key):
        if isinstance(key, str):
            # Column access
            return [row.get(key) for row in self.data]
        return self.data[key]
    
    def __setitem__(self, key, value):
        if isinstance(key, str):
            # Column assignment
            for i, row in enumerate(self.data):
                row[key] = value[i] if isinstance(value, list) else value
    
    def to_dict(self, orient='records'):
        return self.data
    
    def dropna(self, subset=None):
        if subset is None:
            return DataFrame([row for row in self.data if all(v is not None and v != '' for v in row.values())])
        else:
            return DataFrame([row for row in self.data if all(row.get(col) is not None and row.get(col) != '' for col in subset)])
    
    def unique(self):
        """Get unique values from a column"""
        if not self.data:
            return []
        # This is a simplified version - assumes we're calling unique() on a column
        return list(set(self.data))

def read_csv(filepath: str) -> DataFrame:
    """Read CSV file and return DataFrame"""
    data = []
    with open(filepath, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
    return DataFrame(data)

def concat(dataframes: List[List[Dict]], ignore_index: bool = True) -> List[Dict]:
    """Concatenate list of dataframes"""
    result = []
    for df in dataframes:
        result.extend(df)
    return result

def read_sql_query(query: str, conn, params=None, parse_dates=None) -> List[Dict]:
    """Read SQL query and return list of dictionaries"""
    cursor = conn.cursor()
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    
    columns = [description[0] for description in cursor.description]
    data = []
    for row in cursor.fetchall():
        row_dict = dict(zip(columns, row))
        if parse_dates:
            for col in parse_dates:
                if col in row_dict and row_dict[col]:
                    try:
                        row_dict[col] = to_datetime(row_dict[col])
                    except:
                        pass
        data.append(row_dict)
    return data

# Create a mock pandas module
class MockPandas:
    NaT = NaT()
    DataFrame = DataFrame
    
    @staticmethod
    def to_datetime(value):
        return to_datetime(value)
    
    @staticmethod
    def isna(value):
        return isna(value)
    
    @staticmethod
    def read_csv(filepath):
        return read_csv(filepath)
    
    @staticmethod
    def concat(dataframes, ignore_index=True):
        return concat(dataframes, ignore_index)
    
    @staticmethod
    def read_sql_query(query, conn, params=None, parse_dates=None):
        return read_sql_query(query, conn, params, parse_dates)

# Create the pd alias
pd = MockPandas()