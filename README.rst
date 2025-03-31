============
pytest-mimic
============

.. image:: https://img.shields.io/pypi/v/pytest-mimic.svg
    :target: https://pypi.org/project/pytest-mimic
    :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/pytest-mimic.svg
    :target: https://pypi.org/project/pytest-mimic
    :alt: Python versions

.. image:: https://github.com/TCherici/pytest-mimic/actions/workflows/main.yml/badge.svg
    :target: https://github.com/TCherici/pytest-mimic/actions/workflows/main.yml
    :alt: See Build Status on GitHub Actions

Easily record function calls while testing

----

This `pytest`_ plugin was generated with `Cookiecutter`_ along with `@hackebrot`_'s `cookiecutter-pytest-plugin`_ template.


Features
--------

* Record and replay function calls during tests
* Supports async functions
* Easy integration with pytest
* Three usage patterns: fixture-based, configuration-based, and early mimicking via conftest.py
* Deterministic hashing of function calls for reliable replays


Requirements
------------

* Python >= 3.8
* pytest >= 6.2.0
* pytest-asyncio >= 0.24.0


Installation
------------

You can install "pytest-mimic" via `pip`_ from `PyPI`_::

    $ pip install pytest-mimic


Usage
-----

There are three ways to use pytest-mimic:

1. Using the mimic fixture (for functions defined in the test file):

.. code-block:: python

    import pytest
    from my_module import my_api_function

    @pytest.mark.asyncio
    async def test_api_call(mimic):
        # Apply mimicking to the function
        mimic(my_api_function)
        
        # Call the function - it will be recorded or replayed
        result = await my_api_function(arg1, arg2)
        
        assert result["some_key"] == "expected_value"

2. Configuration-based mimicking (recommended):

Configure the functions to mimic in your ``pyproject.toml`` file:

.. code-block:: toml

    # pyproject.toml
    [pytest]
    mimic_functions = [
        "my_module:my_api_function",
        "my_module:another_function"
    ]

Or in ``pytest.ini`` file:

.. code-block:: ini

    # pytest.ini
    [pytest]
    mimic_functions =
        my_module:my_api_function
        my_module:another_function

3. Early mimicking via conftest.py (legacy, deprecated):

.. code-block:: python

    # conftest.py
    from my_module import my_api_function, another_function

    # Define functions to mimic (deprecated approach)
    MIMIC_FUNCTIONS = [
        my_api_function,
        another_function
    ]

Then in your tests:

.. code-block:: python

    # test_example.py
    import pytest
    from my_module import my_api_function

    @pytest.mark.asyncio
    async def test_api_call():
        # The function is already mimicked before this test runs
        result = await my_api_function(arg1, arg2)
        
        assert result["some_key"] == "expected_value"

To record function calls, run pytest with the ``--mimic-record`` flag::

    $ pytest --mimic-record

To replay previously recorded function calls, run pytest without the flag::

    $ pytest

Contributing
------------
Contributions are very welcome. Tests can be run with `tox`_, please ensure
the coverage at least stays the same before you submit a pull request.

License
-------

Distributed under the terms of the `MIT`_ license, "pytest-mimic" is free and open source software


Issues
------

If you encounter any problems, please `file an issue`_ along with a detailed description.

.. _`Cookiecutter`: https://github.com/audreyr/cookiecutter
.. _`@hackebrot`: https://github.com/hackebrot
.. _`MIT`: https://opensource.org/licenses/MIT
.. _`BSD-3`: https://opensource.org/licenses/BSD-3-Clause
.. _`GNU GPL v3.0`: https://www.gnu.org/licenses/gpl-3.0.txt
.. _`Apache Software License 2.0`: https://www.apache.org/licenses/LICENSE-2.0
.. _`cookiecutter-pytest-plugin`: https://github.com/pytest-dev/cookiecutter-pytest-plugin
.. _`file an issue`: https://github.com/TCherici/pytest-mimic/issues
.. _`pytest`: https://github.com/pytest-dev/pytest
.. _`tox`: https://tox.readthedocs.io/en/latest/
.. _`pip`: https://pypi.org/project/pip/
.. _`PyPI`: https://pypi.org/project
