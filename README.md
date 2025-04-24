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
    with pytest_mimic.mimic('module.expensive_function'):
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

## Installation

You can install `pytest-mimic` via pip:

```bash
pip install pytest-mimic
```

## Documentation

For detailed documentation, visit [https://clockworks-data.github.io/pytest-mimic/](https://clockworks-data.github.io/pytest-mimic/) or check the `docs/` directory.

- [Usage Guide](https://clockworks-data.github.io/pytest-mimic/usage/): Basic usage instructions
- [Advanced Features](https://clockworks-data.github.io/pytest-mimic/advanced/): Working with class methods, async functions, and more
- [API Reference](https://clockworks-data.github.io/pytest-mimic/api/): Complete API documentation
- [Examples](https://clockworks-data.github.io/pytest-mimic/examples/): Example usage in different scenarios

## Global Configuration

Configure functions to be mimicked globally in your project configuration:

```toml
# pyproject.toml
[tool.pytest.ini_options]
mimic_functions = [
    "some_module.expensive_function",
    "some_module.another_function",
    "some_module.sub_module.SomeClass.method"
]
```

## CLI Options

- `pytest --mimic-record`: Record function calls during tests
- `pytest --mimic-clear-unused`: Clean up all mimic recordings that weren't used
- `pytest --mimic-fail-on-unused`: Raise an error if any mimic recording was left unused (useful for CI)

## Storage Considerations

The mimic vault directory (`.mimic_vault` by default) can grow large. For Git users, consider using [Git LFS](https://git-lfs.github.com/):

```bash
# Install Git LFS
git lfs install

# Track pickle files in your mimic vault
git lfs track ".mimic_vault/**/*.pkl"

# Commit .gitattributes
git add .gitattributes
```

## Contributing

Contributions are welcome! Tests can be run with [tox](https://tox.readthedocs.io/en/latest/). Please ensure the coverage at least stays the same before submitting a pull request.

## License

Distributed under the terms of the [MIT](https://opensource.org/licenses/MIT) license, `pytest-mimic` is free and open source software.

## Issues

If you encounter any problems, please [file an issue](https://github.com/clockworks-data/pytest-mimic/issues) along with a detailed description.