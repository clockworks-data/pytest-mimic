# API Reference

## Core Functions

### `mimic(func, classmethod_warning=True)`

```python
import pytest_mimic

with pytest_mimic.mimic(expensive_function):
    result = function_that_calls_expensive_function()
```

A context manager that wraps a function or method to intercept its calls and either record or replay its behavior.

**Parameters:**

- `func` (callable): The function or method to mimic
- `classmethod_warning` (bool, optional): Whether to issue a warning when mimicking class methods. Default is `True`.

**Notes:**

- When used with instance methods, `func` must be the method as defined on the class, not a method bound to an instance.
- The context manager will restore the original function when exiting.

## Command Line Options

### `--mimic-record`

Enables record mode, which will execute actual function calls and store their inputs and outputs.

```bash
pytest --mimic-record
```

### `--mimic-clear-unused`

After test execution, cleans up any recordings that weren't used during the test run.

```bash
pytest --mimic-clear-unused
```

### `--mimic-fail-on-unused`

Fails the test run if any recordings weren't used. Useful for CI environments to detect outdated recordings.

```bash
pytest --mimic-fail-on-unused
```

## Configuration Options

### mimic_functions

A list of functions to mimic globally (without needing to use the context manager in tests).

**In pyproject.toml:**

```toml
[tool.pytest.ini_options]
mimic_functions = [
    "some_module:expensive_function",
    "some_module:another_function",
    "some_module.sub_module:SomeClass.method"
]
```

**In pytest.ini:**

```ini
[pytest]
mimic_functions =
    some_module:expensive_function
    some_module:another_function
    some_module.sub_module:SomeClass.method
```

### mimic_vault_path

The directory where recorded function calls will be stored. Default is `.mimic_vault` in the project root.

**In pyproject.toml:**

```toml
[tool.pytest.ini_options]
mimic_vault_path = "custom/path/to/vault"
```

**In pytest.ini:**

```ini
[pytest]
mimic_vault_path = custom/path/to/vault
```

## Internal Functions

These functions are primarily for internal use but may be useful for advanced use cases.

### `compute_hash(func, args, kwargs)`

Computes a deterministic hash for a function call based on the function identity and its inputs.

**Parameters:**

- `func` (callable): The function being called
- `args` (tuple): Positional arguments
- `kwargs` (dict): Keyword arguments

**Returns:**

- `str`: A hex digest that uniquely identifies the function call

### `get_unused_recordings()`

Returns a list of hash keys for recorded function calls that weren't used during the current test run.

**Returns:**

- `list[str]`: A list of hash keys for unused recordings

### `clear_unused_recordings()`

Deletes all recorded function calls that weren't used during the current test run.

**Returns:**

- `int`: The number of recordings that were removed