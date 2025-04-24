import os

import pytest

from pytest_mimic.mimic_manager import (
    _accessed_hashes,
    clear_unused_recordings,
    compute_hash,
    get_unused_recordings,
    mimic,
)


async def async_dummy_func(a, b=2):
    return {"result": a + b}


def sync_dummy_func(a, b=2):
    return {"result": a + b}


class TestMimicManager:
    """Tests for the mimic functions."""

    @pytest.mark.asyncio
    async def test_patching_and_recording(self, tmp_mimic_vault):
        """Test that a function can be patched and its response recorded."""
        # Set record mode
        os.environ["MIMIC_RECORD"] = "1"

        # Verify no files are present
        cache_files = list(tmp_mimic_vault.glob("**/*.pkl"))
        assert len(cache_files) == 0

        with mimic("test_mimic_manager.async_dummy_func"):
            result = await async_dummy_func(5, b=3)

        # Verify result
        assert result == {"result": 8}

        # Verify file was created
        cache_files = list(tmp_mimic_vault.glob("**/*.pkl"))
        assert len(cache_files) > 0

    @pytest.mark.asyncio
    async def test_replaying(self):
        """Test that a function can be replayed from recorded data."""
        # Set record mode for initial recording
        os.environ["MIMIC_RECORD"] = "1"

        with mimic("test_mimic_manager.async_dummy_func"):
            result = await async_dummy_func(5, b=3)

            # Switch to replay mode
            os.environ["MIMIC_RECORD"] = "0"

            new_result = await async_dummy_func(5, b=3)

        assert new_result == result

    @pytest.mark.asyncio
    async def test_missing_mock_exception(self):
        """Test that an exception is raised if no mock is found in replay mode."""
        os.environ["MIMIC_RECORD"] = "0"

        with mimic("test_mimic_manager.async_dummy_func"):
            # Call with args that haven't been recorded should fail
            with pytest.raises(RuntimeError, match="Missing mimic-recorded result for function"):
                await async_dummy_func(999)

    @pytest.mark.asyncio
    async def test_hash_consistency(self):
        """Test that function call hashing is consistent."""
        # Same args should produce same hash
        hash1 = compute_hash(async_dummy_func, (1, 2), {"c": 3})
        hash2 = compute_hash(async_dummy_func, (1, 2), {"c": 3})
        assert hash1 == hash2

        # Different args should produce different hashes
        hash3 = compute_hash(async_dummy_func, (1, 3), {"c": 3})
        assert hash1 != hash3

        # Different kwargs should produce different hashes
        hash4 = compute_hash(async_dummy_func, (1, 2), {"d": 3})
        assert hash1 != hash4

        # Different functions should produce different hashes
        hash5 = compute_hash(sync_dummy_func, (1, 2), {"c": 3})
        assert hash1 != hash5

    @pytest.mark.asyncio
    async def test_clear_unused_recordings(self):
        """Test clearing unused recordings."""
        # Set record mode and create files in the vault
        os.environ["MIMIC_RECORD"] = "1"

        with mimic("test_mimic_manager.async_dummy_func"):
            with mimic("test_mimic_manager.sync_dummy_func"):
                sync_dummy_func(5, b=3)
                sync_dummy_func(5, b=4)
                await async_dummy_func(0, 1)
                await async_dummy_func(0, 2)

                # Reset accessed hashes to simulate a fresh test run
                _accessed_hashes.clear()

                # Access only one of the recordings
                sync_dummy_func(5, b=3)

                # The other recording should be considered unused
                removed = clear_unused_recordings()
                assert removed == 3

    @pytest.mark.asyncio
    async def test_get_unused_recordings(self):
        """Test getting unused recordings."""
        # Set record mode and create files in the vault
        os.environ["MIMIC_RECORD"] = "1"

        # Patch and call the functions to create recordings
        with mimic("test_mimic_manager.async_dummy_func"):
            with mimic("test_mimic_manager.sync_dummy_func"):
                # Record function calls with different args
                sync_dummy_func(5, b=3)
                sync_dummy_func(10, b=20)
                await async_dummy_func(1, b=2)

                # Reset accessed hashes to simulate a fresh test run
                _accessed_hashes.clear()

                # Access only one of the recordings
                sync_dummy_func(5, b=3)

                # Get unused recordings - should include the other recordings
                unused = get_unused_recordings()
                assert len(unused) == 2

    def test_sync_function_mimic(self):
        """Test that sync functions can be mimicked."""
        # Set record mode
        os.environ["MIMIC_RECORD"] = "1"

        # Patch the sync function
        with mimic("test_mimic_manager.sync_dummy_func"):
            # First call to record
            result = sync_dummy_func(5, b=3)
            assert result == {"result": 8}

            # Switch to replay mode
            os.environ["MIMIC_RECORD"] = "0"

            # Call the patched function again
            new_result = sync_dummy_func(5, b=3)

            # Verify result
            assert new_result == result
