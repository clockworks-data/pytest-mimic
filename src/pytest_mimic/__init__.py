"""pytest-mimic - record and replay expensive function calls for faster testing.

This pytest plugin allows you to intercept and record function calls during test execution,
then replay those recordings in subsequent test runs for faster and more stable tests.

Example:
    from pytest_mimic import mimic
    
    def test_expensive_operation():
        with mimic(expensive_function):
            result = function_that_calls_expensive_function()
        assert result == expected_value
"""

from .mimic_manager import mimic

__all__ = ["mimic"]
__version__ = "0.1.0"
