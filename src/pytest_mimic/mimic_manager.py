import hashlib
import inspect
import os
import pickle
from functools import wraps
from pathlib import Path
from typing import Callable, Any

import pytest


class MimicManager:
    """Singleton manager for mimicking function calls."""

    _instance = None

    @classmethod
    def get_instance(cls):
        """Get the singleton instance, raising error if not initialized."""
        if cls._instance is None:
            raise RuntimeError("MockFuncCallManager not initialized. Call initialize() first.")
        return cls._instance

    @classmethod
    def initialize(cls, config: pytest.Config, cache_dir_name: str = ".mimic_vault",
                   forced: bool = False):
        """Initialize the singleton instance."""
        if cls._instance is None or forced:
            cls._instance = cls(config, cache_dir_name, forced)
        return cls._instance

    def __init__(self, config: pytest.Config, cache_dir_name: str, forced: bool):
        """Private constructor, use initialize() instead."""
        if not forced and self._instance is not None:
            raise RuntimeError("Attempting to re-initialize singleton MimicManager."
                               " Use MimicManager.initialize() instead")
        self.mock_cache_dir = config.rootpath.absolute() / cache_dir_name

    def mimic(self, func: Callable):
        """Mimic a function call, returning a mocked result if available."""
        func_module = inspect.getmodule(func)
        original_func = func
        func_name = func.__name__

        @wraps(original_func)
        async def func_wrapper(*args, **kwargs):
            return await self.mimic_func_call(original_func, *args, **kwargs)

        # Mimic the function
        setattr(func_module, func_name, func_wrapper)

    async def mimic_func_call(self, func, *args, **kwargs):
        """Handle a function call, returning a stored result if available."""

        hash_key = self.compute_hash(func, args, kwargs)
        print(f"Hash: {hash_key}")

        try:
            return self.load_stored_result(hash_key)
        except FileNotFoundError:
            record_mode = os.environ.get("RECORD_FUNC_CALLS", "0") == "1"
            if not record_mode:
                raise RuntimeError(f"Missing mimic-recorded result for function call "
                                   f"{func.__name__} with hash {hash_key}.\n"
                                   f"Run pytest with --mimic-record to record responses.")
            # Call the original function
            result = await func(*args, **kwargs)
            # Save the result for future use
            self.save_func_result(hash_key, result)
            return result

    @staticmethod
    def compute_hash(func: Callable, args: tuple, kwargs: dict) -> str:
        """Compute a deterministic hash for a function call."""
        md5 = hashlib.md5()

        # Hash function identity (module + name)
        module_name = inspect.getmodule(func).__name__
        func_name = func.__name__
        md5.update(f"{module_name}.{func_name}".encode("utf-8"))

        # Hash positional arguments using pickle
        for arg in args:
            try:
                pickled_arg = pickle.dumps(arg)
                md5.update(pickled_arg)
            except (pickle.PickleError, TypeError):
                # Fallback if object can't be pickled
                md5.update(str(arg).encode("utf-8"))

        # Hash keyword arguments (sorted by key for determinism)
        for key in sorted(kwargs.keys()):
            md5.update(key.encode("utf-8"))
            try:
                # Use pickle to get a more accurate representation
                pickled_value = pickle.dumps(kwargs[key])
                md5.update(pickled_value)
            except (pickle.PickleError, TypeError):
                # Fallback if object can't be pickled
                md5.update(str(kwargs[key]).encode("utf-8"))

        return md5.hexdigest()

    def load_stored_result(self, hash_key: str) -> Any:
        """Load a saved result from the cache."""
        pickle_file = self.get_model_cache_path(hash_key)

        if not pickle_file.exists():
            raise FileNotFoundError(f"No cached result for hash {hash_key}")

        # Load the result using pickle
        with open(pickle_file, "rb") as f:
            return pickle.load(f)

    def save_func_result(self, hash_key: str, result: Any) -> None:
        """Save a result to the cache."""
        # Ensure the cache directory exists
        self.mock_cache_dir.mkdir(exist_ok=True, parents=True)

        pickle_file = self.get_model_cache_path(hash_key)
        with open(pickle_file, "wb") as f:
            print(f"Saving pickle {hash_key} to {pickle_file}")
            pickle.dump(result, f)

    def get_model_cache_path(self, hash_key: str) -> Path:
        """Get the path to the pickle file for a specific function call."""
        return self.mock_cache_dir / f"{hash_key}.pkl"

    def clear_vault(self):
        if not self.mock_cache_dir.exists():
            return
        for cache in self.mock_cache_dir.iterdir():
            cache.unlink(missing_ok=True)
        self.mock_cache_dir.rmdir()


def mimic_function_call(func: Callable):
    return MimicManager.get_instance().mimic(func)
