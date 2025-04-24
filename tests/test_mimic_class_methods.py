import os

import pytest

from pytest_mimic.mimic_manager import mimic
from tests.example_module import ExampleClass


def test_mimic_fails_on_non_string_paths():
    obj = ExampleClass()
    with pytest.raises(ImportError, match="Failed to import function from path"):
        with mimic(obj.example_method):
            obj.example_method(5, b=3)


def test_mimic_classmethod():
    with mimic("tests.example_module.ExampleClass.example_classmethod"):
        with pytest.raises(RuntimeError, match="Missing mimic-recorded result for function call"):
            ExampleClass.example_classmethod(5, b=3)
        # Set record mode
        os.environ["MIMIC_RECORD"] = "1"
        result = ExampleClass.example_classmethod(5, b=3)
        assert result == 8

        os.environ["MIMIC_RECORD"] = "0"
        assert ExampleClass.example_classmethod(5, b=3) == result


def test_mimic_staticmethod():
    with mimic("tests.example_module.ExampleClass.example_staticmethod"):
        with pytest.raises(RuntimeError, match="Missing mimic-recorded result for function call"):
            ExampleClass.example_staticmethod(5, b=3)
        # Set record mode
        os.environ["MIMIC_RECORD"] = "1"
        result = ExampleClass.example_staticmethod(5, b=3)
        assert result == 8

        os.environ["MIMIC_RECORD"] = "0"
        assert ExampleClass.example_staticmethod(5, b=3) == result


def test_mimic_instance_method():
    with mimic("tests.example_module.ExampleClass.example_method"):
        with pytest.raises(RuntimeError, match="Missing mimic-recorded result for function call"):
            ExampleClass().example_method(5, b=3)
        # Set record mode
        os.environ["MIMIC_RECORD"] = "1"
        result = ExampleClass().example_method(5, b=3)
        assert result == 8

        os.environ["MIMIC_RECORD"] = "0"
        assert ExampleClass().example_method(5, b=3) == result


def test_mimic_mutable_method():
    os.environ["MIMIC_RECORD"] = "1"
    with mimic("tests.example_module.ExampleClass.example_mutable_method"):
        with pytest.raises(RuntimeError, match="has mutated its inputs."):
            ExampleClass().example_mutable_method(5, b=3)


def test_mimic_nested_classmethod():
    with mimic(
        "tests.example_module.ExampleClass.NestedClass.DoubleNestedClass.example_dnested_class"
    ):
        with pytest.raises(RuntimeError, match="Missing mimic-recorded result for function call"):
            ExampleClass.NestedClass.DoubleNestedClass.example_dnested_class(5, b=3)
        # Set record mode
        os.environ["MIMIC_RECORD"] = "1"
        result = ExampleClass.NestedClass.DoubleNestedClass.example_dnested_class(5, b=3)
        assert result == 8

        os.environ["MIMIC_RECORD"] = "0"
        assert ExampleClass.NestedClass.DoubleNestedClass.example_dnested_class(5, b=3) == result


def test_mimic_nested_staticmethod():
    with mimic(
        "tests.example_module.ExampleClass.NestedClass.DoubleNestedClass.example_dnested_staticmethod"
    ):
        with pytest.raises(RuntimeError, match="Missing mimic-recorded result for function call"):
            ExampleClass.NestedClass.DoubleNestedClass.example_dnested_staticmethod(5, b=3)
        # Set record mode
        os.environ["MIMIC_RECORD"] = "1"
        result = ExampleClass.NestedClass.DoubleNestedClass.example_dnested_staticmethod(5, b=3)
        assert result == 8

        os.environ["MIMIC_RECORD"] = "0"
        assert (
            ExampleClass.NestedClass.DoubleNestedClass.example_dnested_staticmethod(5, b=3)
            == result
        )


def test_mimic_nested_instance_method():
    with mimic(
        "tests.example_module.ExampleClass.NestedClass.DoubleNestedClass.example_dnested_method"
    ):
        with pytest.raises(RuntimeError, match="Missing mimic-recorded result for function call"):
            ExampleClass.NestedClass.DoubleNestedClass().example_dnested_method(5, b=3)
        # Set record mode
        os.environ["MIMIC_RECORD"] = "1"
        result = ExampleClass.NestedClass.DoubleNestedClass().example_dnested_method(5, b=3)
        assert result == 8

        os.environ["MIMIC_RECORD"] = "0"
        assert ExampleClass.NestedClass.DoubleNestedClass().example_dnested_method(5, b=3) == result


def test_mimic_class_methods_works(pytester):
    pytester.makeini("""
        [pytest]
        asyncio_default_fixture_loop_scope = "session"
    """)
    pytester.makeconftest(
        """
        from src.pytest_mimic.plugin import _initialize_mimic

        def pytest_configure(config):
            _initialize_mimic(config)

    """
    )
    pytester.makepyfile(
        test_file="""
        import pytest
        from src.pytest_mimic.mimic_manager import mimic

        class ExampleClass:
            def __init__(self):
                self.instance_value = 0

            @classmethod
            def example_classmethod(cls, a, b):
                return a + b

            @staticmethod
            def example_staticmethod(a, b):
                return a + b

            def example_method(self, a, b):
                return self.instance_value + a + b

            def example_mutable_method(self, a, b):
                self.instance_value = self.instance_value + 1
                return self.instance_value + a + b

            class NestedClass:
                class DoubleNestedClass:
                    def __init__(self):
                        self.instance_value = 0

                    @classmethod
                    def example_dnested_classmethod(cls, a, b):
                        return a + b

                    @staticmethod
                    def example_dnested_staticmethod(a, b):
                        return a + b

                    def example_dnested_method(self, a, b):
                        return self.instance_value + a + b

        def test_mimic_classmethod():
            with mimic('test_file.ExampleClass.example_classmethod'):
                result = ExampleClass.example_classmethod(5, b=3)
            assert result == 8

        def test_mimic_staticmethod():
            with mimic('test_file.ExampleClass.example_staticmethod'):
                result = ExampleClass.example_staticmethod(5, b=3)
            assert result == 8

        def test_mimic_instance_method():
            with mimic('test_file.ExampleClass.example_method'):
                result = ExampleClass().example_method(5, b=3)
            assert result == 8

        def test_mimic_mutable_method():
            with mimic('test_file.ExampleClass.example_mutable_method'):
                with pytest.raises(RuntimeError, match="has mutated its inputs."):
                    ExampleClass().example_mutable_method(5, b=3)

        def test_mimic_nested_classmethod():
            with mimic(
                'test_file.ExampleClass.NestedClass.DoubleNestedClass.example_dnested_classmethod'
            ):
                result = ExampleClass.NestedClass.DoubleNestedClass.example_dnested_classmethod(
                    5, b=3)
            assert result == 8

        def test_mimic_nested_staticmethod():
            with mimic(
                'test_file.ExampleClass.NestedClass.DoubleNestedClass.example_dnested_staticmethod'
            ):
                result = ExampleClass.NestedClass.DoubleNestedClass.example_dnested_staticmethod(
                    5, b=3)
            assert result == 8

        def test_mimic_nested_instance_method():
            with mimic(
                'test_file.ExampleClass.NestedClass.DoubleNestedClass.example_dnested_method'
            ):
                result = ExampleClass.NestedClass.DoubleNestedClass().example_dnested_method(5, b=3)
            assert result == 8
        """
    )
    results = pytester.runpytest("-v")

    # All tests should fail since we don't have recordings yet
    assert results.parseoutcomes()["failed"] == 7
    assert "RuntimeError: Missing mim" in "\n".join(results.outlines)

    # now run with record mode on
    results = pytester.runpytest("--mimic-record", "-v")

    # All tests should pass when recording
    assert results.parseoutcomes()["passed"] == 7

    # now run with record mode off again, using stored input-output
    results = pytester.runpytest("-v")

    # All tests should pass with replay
    assert results.parseoutcomes()["passed"] == 7
