import os
import tempfile
from pathlib import Path

import pytest

from src.pytest_mimic import mimic_manager
from src.pytest_mimic.plugin import _mimic_all_functions

pytest_plugins = ["pytester"]


def pytest_configure(config):
    _mimic_all_functions(config)


@pytest.fixture(autouse=True)
def tmp_mimic_vault():
    """Create a mock pytest config for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        mimic_manager.set_cache_dir(Path(tmpdir))
        yield Path(tmpdir)


@pytest.fixture(autouse=True)
def reset_record_mode():
    # Set record mode
    os.environ["MIMIC_RECORD"] = "0"
