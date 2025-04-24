# Examples

This page provides practical examples of using `pytest-mimic` in various testing scenarios.

## Basic Example

Here's a simple example of mimicking a function that makes an API call:

```python
# api.py
import requests

def get_user_data(user_id):
    response = requests.get(f"https://api.example.com/users/{user_id}")
    return response.json()

def process_user_data(user_id):
    user_data = get_user_data(user_id)
    return {
        "name": user_data["name"],
        "email": user_data["email"],
        "processed_at": user_data["updated_at"]
    }
```

```python
# test_user_processing.py
import pytest
import pytest_mimic
from api import get_user_data, process_user_data

def test_process_user_data():
    # Mimic the API call function
    with pytest_mimic.mimic('api.get_user_data'):
        result = process_user_data(user_id=123)
    
    # Assert on the processed result
    assert "name" in result
    assert "email" in result
    assert "processed_at" in result
```

Run the test once with `--mimic-record` to record the actual API call, then run it normally for fast tests without hitting the API.

## Database Query Example

Here's an example with database queries:

```python
# database.py
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

engine = create_engine("postgresql://user:password@localhost/testdb")
Session = sessionmaker(bind=engine)

def get_active_users():
    with Session() as session:
        query = text("SELECT id, name, email FROM users WHERE status = 'active'")
        result = session.execute(query)
        return [dict(row) for row in result]

def count_active_users():
    users = get_active_users()
    return len(users)
```

```python
# test_database.py
import pytest
import pytest_mimic
from database import get_active_users, count_active_users

def test_count_active_users():
    # Mimic the database query function
    with pytest_mimic.mimic('database.get_active_users'):
        count = count_active_users()
    
    # Assert on the count
    assert isinstance(count, int)
    assert count >= 0
```

## Async Function Example

Using `pytest-mimic` with async functions:

```python
# async_api.py
import aiohttp

async def fetch_data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

async def process_multiple_endpoints():
    results = []
    endpoints = ["https://api.example.com/data1", "https://api.example.com/data2"]
    
    for endpoint in endpoints:
        data = await fetch_data(endpoint)
        results.append(data)
    
    return results
```

```python
# test_async_api.py
import pytest
import pytest_mimic
import pytest_asyncio
from async_api import fetch_data, process_multiple_endpoints

@pytest.mark.asyncio
async def test_process_multiple_endpoints():
    # Mimic the async fetch function
    with pytest_mimic.mimic('async_api.fetch_data'):
        results = await process_multiple_endpoints()
    
    # Assert on the results
    assert len(results) == 2
    assert isinstance(results[0], dict)
    assert isinstance(results[1], dict)
```

## Class Method Example

Working with class methods:

```python
# data_processor.py
class DataProcessor:
    @classmethod
    def normalize_data(cls, data):
        # Expensive normalization algorithm
        result = {}
        for key, value in data.items():
            if isinstance(value, str):
                result[key] = value.strip().lower()
            else:
                result[key] = value
        return result
    
    def process(self, data):
        normalized = self.normalize_data(data)
        # Do something with normalized data
        return normalized
```

```python
# test_data_processor.py
import pytest
import pytest_mimic
from data_processor import DataProcessor

def test_process():
    # Mimic the class method
    with pytest_mimic.mimic('data_processor.DataProcessor.normalize_data'):
        processor = DataProcessor()
        result = processor.process({"Name": "John Doe ", "AGE": 30})
    
    # Assert on the result
    assert result["name"] == "john doe"
    assert result["age"] == 30
```

## Global Configuration Example

Using the global configuration to mimic functions:

```toml
# pyproject.toml
[tool.pytest.ini_options]
mimic_functions = [
    "myapp.api.get_user_data",
    "myapp.database.get_active_users",
    "myapp.data_processor.DataProcessor.normalize_data"
]
```

With this configuration, all tests will automatically use the mimicked versions of these functions without needing to add context managers to each test:

```python
# test_various_features.py
from myapp.api import process_user_data
from myapp.database import count_active_users
from myapp.data_processor import DataProcessor

def test_user_processing():
    # get_user_data is automatically mimicked
    result = process_user_data(user_id=123)
    assert "name" in result

def test_user_count():
    # get_active_users is automatically mimicked
    count = count_active_users()
    assert isinstance(count, int)

def test_data_processor():
    # DataProcessor.normalize_data is automatically mimicked
    processor = DataProcessor()
    result = processor.process({"Name": "John Doe"})
    assert result["name"] == "john doe"
```