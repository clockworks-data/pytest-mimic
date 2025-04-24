# pytest-mimic

[![PyPI version](https://img.shields.io/pypi/v/pytest-mimic.svg)](https://pypi.org/project/pytest-mimic)
[![Python versions](https://img.shields.io/pypi/pyversions/pytest-mimic.svg)](https://pypi.org/project/pytest-mimic)
[![See Build Status on GitHub Actions](https://github.com/clockworks-data/pytest-mimic/actions/workflows/main.yml/badge.svg)](https://github.com/clockworks-data/pytest-mimic/actions/workflows/main.yml)

---

`pytest-mimic` is a pytest plugin to record and replay expensive function or method calls for faster and cleaner unit testing. It enables you to:

- Speed up tests that rely on expensive operations (API calls, database queries, etc.)
- Create more reliable tests that don't depend on external services
- Reduce complexity in your test setup

## Quick Start

```python
import pytest_mimic

def test_function_to_test():
    # Wrap the expensive function in a mimic context manager
    with pytest_mimic.mimic('module.sub_module.expensive_function'):
       result = function_to_test()  # This function calls expensive_function internally
    assert result == expected_value
```

1. Run your tests with recording enabled: `pytest --mimic-record`
2. For subsequent runs, just use `pytest` to utilize the stored outputs

## Key Features

- Record and replay function calls with identical input/output behavior
- Support for both synchronous and asynchronous functions
- Works with regular functions, class methods, static methods, and instance methods
- Global configuration to mimic functions throughout your test suite
- CLI options for managing recorded function calls
- Detects and prevents issues with functions that mutate their inputs

## Documentation

This documentation provides comprehensive information about using `pytest-mimic`:

- [Usage Guide](usage.md): Basic usage instructions
- [Advanced Features](advanced.md): Working with class methods, async functions, and more
- [API Reference](api.md): Complete API documentation
- [Examples](examples.md): Example usage in different scenarios