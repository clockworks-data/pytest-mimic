import os
import tempfile
from pathlib import Path

import pytest

from pytest_mimic import mimic_manager

pytest_plugins = ["pytester"]


@pytest.fixture(autouse=True)
def tmp_mimic_vault():
    """Create a temporary directory for mimic recordings during tests.
    
    This fixture creates a temporary directory to use as the mimic vault
    for each test, ensuring tests don't interfere with each other by
    sharing recordings.
    
    Returns:
        Path: The path to the temporary mimic vault directory
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        mimic_manager.set_cache_dir(Path(tmpdir))
        yield Path(tmpdir)


@pytest.fixture(autouse=True)
def reset_record_mode():
    """Reset the mimic record mode before each test.
    
    This fixture ensures that tests start with recording disabled
    unless they explicitly enable it, preventing accidental recording.
    """
    # Set record mode to off by default
    os.environ["MIMIC_RECORD"] = "0"
