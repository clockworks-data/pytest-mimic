import pytest

from src.pytest_mimic.mimic_manager import MimicManager
from src.pytest_mimic.plugin import _mimic_all_functions

from tests.example_module import example_function_to_mimic

pytest_plugins = ["pytester"]

MIMIC_FUNCTIONS = [example_function_to_mimic]


def pytest_configure(config):

    _mimic_all_functions(config)


@pytest.fixture(scope='function', autouse=True)
def clean_mimic_vault():
    yield
    MimicManager.get_instance().clear_vault()
