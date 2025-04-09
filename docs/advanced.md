# Advanced Features

## Working with Class Methods

`pytest-mimic` can mimic class methods, including both instance methods, classmethods and staticmethods. There are some important considerations when mimicking methods:

### Class Methods and Static Methods

Class methods and static methods can be mimicked directly:

```python
import pytest_mimic

def test_classmethod():
    with pytest_mimic.mimic(MyClass.class_method):
        result = code_that_calls_class_method()
    assert result == expected_result

def test_staticmethod():
    with pytest_mimic.mimic(MyClass.static_method):
        result = code_that_calls_static_method()
    assert result == expected_result
```

### Instance Methods

When mimicking instance methods, you must mimic the class method definition, not a method bound to an instance:

```python
# CORRECT: Mimic the class method definition
with pytest_mimic.mimic(MyClass.instance_method):
    result = function_that_calls_instance_method()

# INCORRECT: Will raise an error
instance = MyClass()
with pytest_mimic.mimic(instance.instance_method):  # This will raise an error
    result = function_that_calls_instance_method()
```

### Method Mutation Warning

When mimicking class methods, the plugin will issue a warning about potential class mutations. This is because class methods can potentially modify the class state, which could lead to inconsistent test behavior.

If you're sure your class method doesn't mutate the class state, you can suppress this warning:

```python
with pytest_mimic.mimic(MyClass.class_method, classmethod_warning=False):
    result = function_that_calls_class_method()
```

## Handling Mutable Objects

`pytest-mimic` tracks input mutations to prevent inconsistent behavior. If a mimicked function mutates its inputs (arguments or the instance it's called on), the plugin will raise an error.

For example:

```python
def mutating_function(a_list):
    a_list.append(1)  # Mutates the input list
    return sum(a_list)

def test_mutating_function():
    test_list = [1, 2, 3]
    with pytest_mimic.mimic(mutating_function):
        result = mutating_function(test_list)  # This will raise an error in record mode
```

The error occurs because the input list changes during function execution, which could lead to inconsistent behavior when replaying the recorded function call.

## Customizing the Mimic Vault Location

By default, `pytest-mimic` stores recorded function calls in the `.mimic_vault` directory in your project root. You can customize this location:

### In pyproject.toml:

```toml
[tool.pytest.ini_options]
mimic_vault_path = "custom/path/to/vault"
```

### In pytest.ini:

```ini
[pytest]
mimic_vault_path = custom/path/to/vault
```

## Managing Large Mimic Vaults

The mimic vault can grow quite large if you're recording functions that return large data structures. Here are some strategies for managing this:

### Use Git LFS

If you're using Git, consider using [Git Large File Storage (LFS)](https://git-lfs.github.com/) to handle large pickle files:

```bash
# Install Git LFS
git lfs install

# Track pickle files in your mimic vault
git lfs track ".mimic_vault/**/*.pkl"

# Make sure .gitattributes is committed
git add .gitattributes
```

### Clean Up Unused Recordings

Regularly clean up unused recordings to keep the vault size manageable:

```bash
pytest --mimic-clear-unused
```

You can also enforce this as part of your CI process by using the `--mimic-fail-on-unused` flag to detect when recordings are no longer needed.

## Working with Async Functions

`pytest-mimic` fully supports async functions, both when mimicking them directly and when mimicking functions that call async functions:

```python
import pytest_mimic
import pytest

@pytest.mark.asyncio
async def test_async_function():
    with pytest_mimic.mimic(expensive_async_function):
        result = await function_that_calls_expensive_async_function()
    assert result == expected_result
```

The plugin automatically detects whether a function is async or sync and handles it appropriately.