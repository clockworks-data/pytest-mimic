============
pytest-mimic
============

.. image:: https://img.shields.io/pypi/v/pytest-mimic.svg
    :target: https://pypi.org/project/pytest-mimic
    :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/pytest-mimic.svg
    :target: https://pypi.org/project/pytest-mimic
    :alt: Python versions

.. image:: https://github.com/clockworks-data/pytest-mimic/actions/workflows/main.yml/badge.svg
    :target: https://github.com/clockworks-data/pytest-mimic/actions/workflows/main.yml
    :alt: See Build Status on GitHub Actions

Are you bored with hand-mocking expensive function calls?
Or wasting time recreating model outputs and
ending up with brittle tests?

Have your mocks ever fooled you, running successful tests whilst silently ignoring unexpected changes in their inputs?

`pytest-mimic` is a pytest plugin to record and replay expensive function calls for better, faster and cleaner unit testing.

Use cases
--------

- testing a pipeline that runs some ML model which require beefy hardware to run
- testing functions that would make calls to some external API
- testing code that requires access to an X-server which is not available in CI

Features
--------

* Record and replay function calls during tests
* Supports sync and async functions
* Deterministic hashing of function calls & pickling of function outputs


This `pytest`_ plugin was generated with `Cookiecutter`_ along with `@hackebrot`_'s `cookiecutter-pytest-plugin`_ template.


Installation
------------

You can install "pytest-mimic" via `pip`_ from `PyPI`_::

    $ pip install pytest-mimic


Usage
-----

Configure the functions to mimic in your ``pyproject.toml`` file:

.. code-block:: toml

    # pyproject.toml
    [tool.pytest.ini_options]
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


Run tests once with the --mimic-record flag (`pytest --mimic-record`) to run the mimicked functions
 and store their outputs.
All subsequent test runs will return the mimicked functions' output directly.

To record function calls, run pytest with the ``--mimic-record`` flag::

    $ pytest --mimic-record

To replay previously recorded function calls, run pytest without the flag::

    $ pytest

To clean up unused recordings after a test run, use the ``--mimic-clear-unused`` flag::

    $ pytest --mimic-clear-unused

This will remove any recordings in the vault that weren't accessed during the test run, helping keep your vault clean and reducing its size.

To fail the test run if any recordings weren't used, use the ``--mimic-fail-on-unused`` flag::

    $ pytest --mimic-fail-on-unused

This is useful in CI pipelines to detect when recordings have become stale or are no longer needed.

Storage Considerations
~~~~~~~~~~~~~~~~~~~~~

The mimic vault directory (``.mimic_vault`` by default) contains pickle files that can be large, especially when recording complex API responses. For optimal storage and version control:

1. **Git LFS**: Use `Git Large File Storage (LFS) <https://git-lfs.github.com/>`_ to efficiently handle these files:

   .. code-block:: bash

       # Install Git LFS
       $ git lfs install
       
       # Track pickle files in your mimic vault
       $ git lfs track ".mimic_vault/**/*.pkl"
       
       # Make sure .gitattributes is committed
       $ git add .gitattributes
       
2. **Custom Storage Location**: You can specify a custom location for the mimic vault:

   .. code-block:: toml
   
       # pyproject.toml
       [tool.pytest.ini_options]
       mimic_vault_path = "path/to/mimic_storage"

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
.. _`file an issue`: https://github.com/clockworks-data/pytest-mimic/issues
.. _`pytest`: https://github.com/pytest-dev/pytest
.. _`tox`: https://tox.readthedocs.io/en/latest/
.. _`pip`: https://pypi.org/project/pip/
.. _`PyPI`: https://pypi.org/project
