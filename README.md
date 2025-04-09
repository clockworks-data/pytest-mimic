# pytest-mimic

[![PyPI version](https://img.shields.io/pypi/v/pytest-mimic.svg)](https://pypi.org/project/pytest-mimic)
[![Python versions](https://img.shields.io/pypi/pyversions/pytest-mimic.svg)](https://pypi.org/project/pytest-mimic)
[![See Build Status on GitHub Actions](https://github.com/clockworks-data/pytest-mimic/actions/workflows/main.yml/badge.svg)](https://github.com/clockworks-data/pytest-mimic/actions/workflows/main.yml)

---

`pytest-mimic` is a pytest plugin to record and replay expensive function or method calls for faster and cleaner unit testing.

## Usage
Suppose you want to test the workings of a function that calls some expensive function.
You can mimic the expensive function like this:

```python
def test_function_to_test():
    with pytest_mimic.mimic(expensive_function):
       result = function_to_test()
    assert result == 1
```

Run `pytest --mimic-record` once to run tests calling the mimicked functions and storing their outputs.

Afterward all `pytest` runs will utilize the stored output, as long as the function and inputs don't change.

### Mimic functions globally
Instead of mimicking expensive functions or methods for every test you write, you can configure the functions to mimic in your `pyproject.toml` file:

```toml
# pyproject.toml
[tool.pytest.ini_options]
mimic_functions = [
    "some_module:expensive_function",
    "some_module:another_function",
    "some_module.sub_module:SomeClass.method"
]
```

or in `pytest.ini` file:

```ini
# pytest.ini
[pytest]
mimic_functions =
    some_module:expensive_function
    some_module:another_function
    some_module.sub_module:SomeClass.method
```

This will ensure that all calls to those functions or methods will be mimicked.

### CLI options

- `pytest --mimic-record`: record function calls
- `pytest --mimic-clear-unused`: after the run completes, clean up all mimic recordings that were not used
- `pytest --mimic-fail-on-unused`: raises an error if any mimic recording was left unused. Useful for CI


## Installation

You can install "pytest-mimic" via [pip](https://pypi.org/project/pip/) from [PyPI](https://pypi.org/project):

```
$ pip install pytest-mimic
```

## Storage Considerations

The mimic vault directory (`project_root/.mimic_vault` by default) can grow to contain a large amount of data depending on the amount of mimicked calls and size of outputs.

Consider using something like [Git Large File Storage (LFS)](https://git-lfs.github.com/) to efficiently handle these files:

   ```bash
   # Install Git LFS
   $ git lfs install
   
   # Track pickle files in your mimic vault
   $ git lfs track ".mimic_vault/**/*.pkl"
   
   # Make sure .gitattributes is committed
   $ git add .gitattributes
   ```


## Contributing

Contributions are very welcome. Tests can be run with [tox](https://tox.readthedocs.io/en/latest/), please ensure the coverage at least stays the same before you submit a pull request.

## License

Distributed under the terms of the [MIT](https://opensource.org/licenses/MIT) license, "pytest-mimic" is free and open source software

This [pytest](https://github.com/pytest-dev/pytest) plugin was generated with [Cookiecutter](https://github.com/audreyr/cookiecutter) along with [@hackebrot](https://github.com/hackebrot)'s [cookiecutter-pytest-plugin](https://github.com/pytest-dev/cookiecutter-pytest-plugin) template.

## Issues

If you encounter any problems, please [file an issue](https://github.com/clockworks-data/pytest-mimic/issues) along with a detailed description.