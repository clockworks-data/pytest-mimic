import asyncio
import hashlib
import importlib
import inspect
import os
import pickle
import sys
import warnings
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Optional

# Global state
_cache_dir: Optional[Path] = None


def set_cache_dir(path: Path):
    global _cache_dir
    _cache_dir = path


def get_cache_dir() -> Path:
    """Get the mimic cache directory path."""
    if _cache_dir is None:
        raise RuntimeError("Mimic functionality not initialized. Initialize first.")
    return _cache_dir


def mimic(func: Callable) -> None:
    """
    Mimic a function call, replacing it with a version that returns recorded results.

    This is the main entry point for mimicking a function. Works with both sync and async functions.
    """
    func_module = inspect.getmodule(func)
    original_func = func
    func_name = func.__name__
    is_async = asyncio.iscoroutinefunction(original_func)

    if is_async:
        @wraps(original_func)
        async def async_wrapper(*args, **kwargs):
            return await mimic_async_func_call(original_func, *args, **kwargs)

        # Replace the function with our async wrapper
        setattr(func_module, func_name, async_wrapper)
    else:
        @wraps(original_func)
        def sync_wrapper(*args, **kwargs):
            return mimic_sync_func_call(original_func, *args, **kwargs)

        # Replace the function with our sync wrapper
        setattr(func_module, func_name, sync_wrapper)


async def mimic_async_func_call(func: Callable, *args, **kwargs) -> Any:
    """Handle an async function call, returning a stored result if available."""
    hash_key = compute_hash(func, args, kwargs)
    print(f"Hash: {hash_key}")

    try:
        return load_stored_result(hash_key)
    except FileNotFoundError as err:
        record_mode = os.environ.get("MIMIC_RECORD", "0") == "1"
        if not record_mode:
            raise RuntimeError(f"Missing mimic-recorded result for function call "
                               f"{func.__name__} with hash {hash_key}.\n"
                               f"Run pytest with --mimic-record to record responses.") from err
        # Call the original function
        result = await func(*args, **kwargs)
        # Save the result for future use
        save_func_result(hash_key, result)
        return result


def mimic_sync_func_call(func: Callable, *args, **kwargs) -> Any:
    """Handle a synchronous function call, returning a stored result if available."""
    hash_key = compute_hash(func, args, kwargs)
    print(f"Hash: {hash_key}")

    try:
        return load_stored_result(hash_key)
    except FileNotFoundError as err:
        record_mode = os.environ.get("MIMIC_RECORD", "0") == "1"
        if not record_mode:
            raise RuntimeError(f"Missing mimic-recorded result for function call "
                               f"{func.__name__} with hash {hash_key}.\n"
                               f"Run pytest with --mimic-record to record responses.") from err
        # Call the original function
        result = func(*args, **kwargs)
        # Save the result for future use
        save_func_result(hash_key, result)
        return result


def compute_hash(func: Callable, args: tuple, kwargs: dict) -> str:
    """Compute a deterministic hash for a function call."""
    md5 = hashlib.md5()

    # Hash function identity (module + name)
    module_name = inspect.getmodule(func).__name__
    func_name = func.__name__
    md5.update(f"{module_name}.{func_name}".encode())

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


def load_stored_result(hash_key: str) -> Any:
    """Load a saved result from the cache."""
    pickle_file = get_model_cache_path(hash_key)

    if not pickle_file.exists():
        raise FileNotFoundError(f"No cached result for hash {hash_key}")

    # Load the result using pickle
    with open(pickle_file, "rb") as f:
        return pickle.load(f)


def save_func_result(hash_key: str, result: Any) -> None:
    """Save a result to the cache."""
    # Ensure the cache directory exists
    cache_dir = get_cache_dir()
    cache_dir.mkdir(exist_ok=True, parents=True)

    pickle_file = get_model_cache_path(hash_key)
    with open(pickle_file, "wb") as f:
        print(f"Saving pickle {hash_key} to {pickle_file}")
        pickle.dump(result, f)


def get_model_cache_path(hash_key: str) -> Path:
    """Get the path to the pickle file for a specific function call."""
    return get_cache_dir() / f"{hash_key}.pkl"


def clear_vault() -> None:
    """Clear all stored function call results."""
    cache_dir = get_cache_dir()
    if not cache_dir.exists():
        return
    for cache in cache_dir.iterdir():
        cache.unlink(missing_ok=True)
    cache_dir.rmdir()


def _mimic_all_functions(config):
    """Initialize the mimic system and return the cache directory path."""
    if config.getini('mimic_vault_path'):
        cache_dir = Path(config.getini('mimic_vault_path')).absolute()
    else:
        cache_dir = config.rootpath.absolute() / ".mimic_vault"

    set_cache_dir(cache_dir)

    # Apply mimicking to all functions from ini configuration
    functions_to_mimic = _get_functions_to_mimic(config)
    for func in functions_to_mimic:
        mimic(func)


def _get_functions_to_mimic(config):
    """Get functions to mimic from configuration.

    Reads functions from mimic_functions ini configuration
    """
    functions_to_mimic = []

    # Get functions from ini configuration
    mimic_function_imports = config.getini('mimic_functions')
    for import_path in mimic_function_imports:
        func = _import_function_from_string(import_path, config.rootpath)
        if func is not None:
            functions_to_mimic.append(func)

    return functions_to_mimic


def _import_function_from_string(import_path, pytest_config_root_path):
    """Import a function from an import path string.

    Format: module.submodule:function_name
    Example: tests.example_module:example_function_to_mimic
    """
    try:
        if ':' not in import_path:
            raise ValueError(f"Invalid import path format: {import_path}."
                             f" Expected 'module:function'")

        module_path, func_name = import_path.strip().split(':', 1)

        sys.path.append(str(pytest_config_root_path))

        # Import the module
        module = importlib.import_module(module_path)

        # Get the function from the module
        if not hasattr(module, func_name):
            raise ValueError(f"Function '{func_name}' not found in module '{module_path}'")

        return getattr(module, func_name)

    except (ImportError, AttributeError, ValueError) as e:
        warnings.warn(f"Failed to import function from '{import_path}': {e}", stacklevel=2)
        return None
