# Welcome to pytest-mimic

Easily record function calls while testing

## Overview

pytest-mimic is a pytest plugin that allows you to record and replay function calls, particularly useful for testing code that makes external API calls or other network requests without hitting the external service in most test runs.

## Installation

```bash
pip install pytest-mimic
```

## Basic Usage

### Method 1: Using the mimic fixture

```python
# test_example.py
import pytest
from my_module import my_api_function

@pytest.mark.asyncio
async def test_api_call(mimic):
    # Apply mimicking to the function
    mimic(my_api_function)
    
    # Call the function - it will be recorded or replayed
    result = await my_api_function(arg1, arg2)
    
    assert result["some_key"] == "expected_value"
```

### Method 2: Configuration-based mimicking (recommended)

Configure the functions to mimic in your `pyproject.toml` or `pytest.ini` file:

```toml
# pyproject.toml
[pytest]
mimic_functions = [
    "my_module:my_api_function",
    "my_module:another_function"
]
```

Or in pytest.ini:

```ini
# pytest.ini
[pytest]
mimic_functions =
    my_module:my_api_function
    my_module:another_function
```

### Method 3: Early mimicking in conftest.py (legacy, deprecated)

```python
# conftest.py
from my_module import my_api_function, another_function

# Define functions to mimic - these will be mimicked early during pytest configuration
# Note: This method is deprecated and will be removed in a future version
MIMIC_FUNCTIONS = [
    my_api_function,
    another_function
]
```

Then in your tests, you can directly use the functions:

```python
# test_example.py
import pytest
from my_module import my_api_function

@pytest.mark.asyncio
async def test_api_call():
    # The function is already mimicked before this test runs
    result = await my_api_function(arg1, arg2)
    
    assert result["some_key"] == "expected_value"
```

## Recording vs Replaying

- To record function calls, run pytest with the `--mimic-record` flag:
  ```
  pytest --mimic-record
  ```

- To replay previously recorded function calls, run pytest without the flag:
  ```
  pytest
  ```

- To clean up unused recordings from the vault, run pytest with the `--mimic-clear-unused` flag:
  ```
  pytest --mimic-clear-unused
  ```
  This will remove any recordings that weren't accessed during the test run, helping keep your vault clean and reducing storage requirements.

- To fail the test run if any recordings weren't used, run pytest with the `--mimic-fail-on-unused` flag:
  ```
  pytest --mimic-fail-on-unused
  ```
  This is useful in CI pipelines to detect when recordings have become stale or are no longer needed.

## How It Works

1. When run with `--mimic-record`, actual function calls are made and results are stored
2. When run without the flag, function calls are intercepted and previously recorded results are returned
3. Function calls are hashed based on the function name, module, and arguments

This allows you to run your tests against real APIs once to record the responses, then run subsequent tests against the recorded data for speed and reliability.
