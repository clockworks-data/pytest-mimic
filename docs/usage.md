# Usage Guide

`pytest-mimic` is a pytest plugin that allows you to record and replay expensive function or method calls. This can significantly speed up tests that depend on slow operations like API calls, database queries, or complex computations.

## Basic Usage

### Step 1: Install the package

```bash
pip install pytest-mimic
```

### Step 2: Add mimic context managers to your tests

Wrap expensive function calls with the `mimic` context manager in your test:

```python
import pytest_mimic

def test_my_function():
    with pytest_mimic.mimic(expensive_function):
        result = function_that_calls_expensive_function()
    assert result == expected_result
```

### Step 3: Record function calls

Run your tests with the `--mimic-record` option to record the function calls:

```bash
pytest --mimic-record
```

This will execute the actual expensive functions and store their inputs and outputs.

### Step 4: Run tests with recorded data

Run your tests normally without the `--mimic-record` option:

```bash
pytest
```

The plugin will intercept calls to the mimicked functions and return the previously recorded results instead of executing the actual functions.

## Global Configuration

Instead of adding the mimic context manager to each test, you can configure functions to be mimicked globally in your `pyproject.toml` or `pytest.ini` file.

### Configure in pyproject.toml

```toml
[tool.pytest.ini_options]
mimic_functions = [
    "some_module:expensive_function",
    "some_module:another_function", 
    "some_module.sub_module:SomeClass.method"
]
# Optional: specify custom location for mimic cache directory
# mimic_vault_path = ".mimic_vault"
```

### Configure in pytest.ini

```ini
[pytest]
mimic_functions =
    some_module:expensive_function
    some_module:another_function
    some_module.sub_module:SomeClass.method
# Optional: specify custom location for mimic vault
# mimic_vault_path = .mimic_vault
```

## Command Line Options

`pytest-mimic` provides several command line options:

- `--mimic-record`: Record function calls during test execution
- `--mimic-clear-unused`: Clear unused recordings after the test run completes
- `--mimic-fail-on-unused`: Fail the test run if any recordings were not used (useful for CI)

Example:

```bash
# Record function calls and clear unused recordings
pytest --mimic-record --mimic-clear-unused

# Run tests with recorded data and fail if any recordings are unused
pytest --mimic-fail-on-unused
```

## Handling Different Arguments

The plugin generates a unique hash for each function call based on:
- The function identity (module and name)
- The positional arguments
- The keyword arguments

If a function is called with the same arguments in a test, the recorded result will be used. If it's called with different arguments, you'll need to record those calls too.