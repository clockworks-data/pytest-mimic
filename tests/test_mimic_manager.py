import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.pytest_mimic.mimic_manager import MimicManager, mimic_function_call


# Test async function to mock
async def dummy_func(a, b=2):
    return {"result": a + b}


async def dummy_func_2(a, b=2):
    return {"result": a + b}


@pytest.fixture(scope='session')
def mock_config():
    """Create a mock pytest config for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_path = Path(tmpdir)
        mock_config = MagicMock()
        mock_config.rootpath = temp_path
        # Force initialize the singleton for testing
        MimicManager.initialize(mock_config, forced=True)
        yield mock_config


class TestMimicManager:
    """Tests for the MimicManager class."""

    @pytest.mark.asyncio
    async def test_patching_and_recording(self, mock_config):
        """Test that a function can be patched and its response recorded."""
        # Set record mode
        os.environ["RECORD_FUNC_CALLS"] = "1"

        # Verify no files are present
        cache_files = list(mock_config.rootpath.glob("**/*.pkl"))
        assert len(cache_files) == 0

        mimic_function_call(dummy_func)

        # Call the patched function
        result = await dummy_func(5, b=3)

        # Verify result
        assert result == {"result": 8}

        # Verify file was created
        cache_files = list(mock_config.rootpath.glob("**/*.pkl"))
        assert len(cache_files) > 0

    @pytest.mark.asyncio
    async def test_replaying(self):
        """Test that a function can be replayed from recorded data."""
        # Set record mode for initial recording
        os.environ["RECORD_FUNC_CALLS"] = "1"

        # Patch function
        mimic_function_call(dummy_func)

        # First call to record
        result = await dummy_func(5, b=3)

        # Switch to replay mode
        os.environ["RECORD_FUNC_CALLS"] = "0"

        # Call the patched function again
        new_result = await dummy_func(5, b=3)

        # Verify result
        assert new_result == result

    @pytest.mark.asyncio
    async def test_missing_mock_exception(self):
        """Test that an exception is raised if no mock is found in replay mode."""
        os.environ["RECORD_FUNC_CALLS"] = "0"

        # Patch using the function API
        mimic_function_call(dummy_func)

        # Call with args that haven't been recorded should fail
        with pytest.raises(RuntimeError, match="Missing mimic-recorded result for function call"):
            await dummy_func(999)

    @pytest.mark.asyncio
    async def test_hash_consistency(self):
        """Test that function call hashing is consistent."""
        # Same args should produce same hash
        hash1 = MimicManager.compute_hash(dummy_func, (1, 2), {"c": 3})
        hash2 = MimicManager.compute_hash(dummy_func, (1, 2), {"c": 3})
        assert hash1 == hash2

        # Different args should produce different hashes
        hash3 = MimicManager.compute_hash(dummy_func, (1, 3), {"c": 3})
        assert hash1 != hash3

        # Different kwargs should produce different hashes
        hash4 = MimicManager.compute_hash(dummy_func, (1, 2), {"d": 3})
        assert hash1 != hash4

        # Different functions should produce different hashes
        hash5 = MimicManager.compute_hash(dummy_func_2, (1, 2), {})
        assert hash1 != hash5

    def test_singleton_pattern(self, mock_config):
        """Test that the singleton pattern works as expected."""
        # Initialize twice should return the same instance
        instance1 = MimicManager.get_instance()
        instance2 = MimicManager.get_instance()

        assert instance1 is instance2

        # Calling initialize again should return the existing instance
        instance3 = MimicManager.initialize(mock_config)
        assert instance1 is instance3
