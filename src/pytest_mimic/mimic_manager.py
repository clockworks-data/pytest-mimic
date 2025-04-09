import asyncio
import contextlib
import hashlib
import importlib
import inspect
import logging
import os
import pickle
import sys
import types
import warnings
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Optional, Union

logger = logging.getLogger("pytest_mimic")

_cache_dir: Optional[Path] = None
_accessed_hashes: set = set()


def set_cache_dir(path: Path):
    global _cache_dir
    _cache_dir = path


def get_cache_dir() -> Path:
    """Get the mimic cache directory path."""
    if _cache_dir is None:
        raise RuntimeError("Mimic functionality not initialized. Initialize first.")
    return _cache_dir


def try_load_result_from_cache(func, args, kwargs) -> tuple[Optional[object], Optional[str]]:
    """
        Tries to load function call from mimic vault. If it fails and is in mimic-record mode return
         the function call hash key instead to allow for the storage of the function output
    """
    hash_key = compute_hash(func, args, kwargs)

    global _accessed_hashes
    # Track which hashes are accessed during this test run
    _accessed_hashes.add(hash_key)
    pickle_file = get_model_cache_path(hash_key)
    record_mode = os.environ.get("MIMIC_RECORD", "0") == "1"
    # Load the result using pickle
    if pickle_file.exists():
        with open(pickle_file, "rb") as f:
            return pickle.load(f), None

    if not record_mode:
        raise RuntimeError(f"Missing mimic-recorded result for function call "
                           f"{func.__name__} with hash {hash_key}.\n"
                           f"Run pytest with --mimic-record to record responses.")
    return None, hash_key


def mimic_location(func_location: str) -> None:
    """
    Mimic a function call, replacing it with a version that returns recorded results.

    This is the main entry point for mimicking a function. Works with both sync and async functions.
    """
    parent_obj, func = _import_function_from_string(func_location)

    _mimic(parent_obj, func)


@contextlib.contextmanager
def mimic(func: callable, classmethod_warning: bool = True):
    original_func = func

    if inspect.ismethod(func):
        if not isinstance(func.__self__, type):
            raise ValueError(f"It is not possible to mimic methods of instantiated objects. \n"
                             f"Mimic the class definition of the method instead:\n"
                             f"`with mimic(MyClass.method):` instead of "
                             f"`with mimic(MyClass().method):`")

        if classmethod_warning:
            warnings.warn(f"Mimicking classmethod {func.__qualname__}.\n"
                          f"Mimicking cannot check for class-level mutations caused"
                          f" by calling this method.\n"
                          f"If you're sure that this classmethod does not mutate its class"
                          f" you can use\n"
                          f"\tmimic(<your_classmethod>, classmethod_warning=False)\n"
                          f"to suppress this warning.")
        func_parent = func.__self__

    elif '.' in func.__qualname__:
        #  static methods are not recognized as methods,
        #   but we need to get their parent class nonetheless
        func_parent = importlib.import_module(func.__module__)
        for child in func.__qualname__.split('.')[:-1]:
            func_parent = getattr(func_parent, child)
    else:
        func_parent = importlib.import_module(func.__module__)

    _mimic(func_parent, func)
    yield
    setattr(func_parent, original_func.__name__, func)


def _mimic(parent_obj, func):
    if asyncio.iscoroutinefunction(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            result, hash_key = try_load_result_from_cache(func, args, kwargs)

            if hash_key:
                # Call the original function
                result = await func(*args, **kwargs)

                # Check that calling the function didn't mutate inputs
                new_hash_key = compute_hash(func, args, kwargs)
                if new_hash_key != hash_key:
                    raise RuntimeError(f"Running function {func} has mutated its inputs.\n"
                                       f"Mimicking shouldn't be used on functions or methods"
                                       f" that mutate its input (or parent object)")

                # Save the result for future use
                save_func_result(hash_key, result)

            return result

        setattr(parent_obj, func.__name__, async_wrapper)
    else:
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            result, hash_key = try_load_result_from_cache(func, args, kwargs)

            if hash_key:
                # Call the original function
                result = func(*args, **kwargs)

                # Check that calling the function didn't mutate inputs
                new_hash_key = compute_hash(func, args, kwargs)
                if new_hash_key != hash_key:
                    raise RuntimeError(f"Running function {func} has mutated its inputs.\n"
                                       f"Mimicking shouldn't be used on functions or methods"
                                       f" that mutate its input (or parent object)")

                # Save the result for future use
                save_func_result(hash_key, result)

            return result

        setattr(parent_obj, func.__name__, sync_wrapper)


def compute_hash(func: Callable, args: tuple, kwargs: dict) -> str:
    """Compute a deterministic hash for a function call."""
    sha256 = hashlib.sha256()

    # Hash function identity (module + name)
    module_name = inspect.getmodule(func).__name__
    func_name = func.__name__
    sha256.update(f"{module_name}.{func_name}".encode())

    # Hash positional arguments using pickle
    for arg in args:
        try:
            pickled_arg = pickle.dumps(arg)
            sha256.update(pickled_arg)
        except (pickle.PickleError, TypeError):
            # Fallback if object can't be pickled
            sha256.update(str(arg).encode("utf-8"))

    # Hash keyword arguments (sorted by key for determinism)
    for key in sorted(kwargs.keys()):
        sha256.update(key.encode("utf-8"))
        try:
            # Use pickle to get a more accurate representation
            pickled_value = pickle.dumps(kwargs[key])
            sha256.update(pickled_value)
        except (pickle.PickleError, TypeError):
            # Fallback if object can't be pickled
            sha256.update(str(kwargs[key]).encode("utf-8"))

    hash_key = sha256.hexdigest()
    logger.debug(f"Mimic: function {func.__name__} with inputs {args} and {kwargs}"
                 f" generated hash {hash_key}")

    return hash_key


def save_func_result(hash_key: str, result: Any) -> None:
    """Save a result to the cache."""
    global _accessed_hashes
    # Track this hash as it's being created in this test run
    _accessed_hashes.add(hash_key)

    # Ensure the cache directory exists
    cache_dir = get_cache_dir()
    cache_dir.mkdir(exist_ok=True, parents=True)

    pickle_file = get_model_cache_path(hash_key)
    with open(pickle_file, "wb") as f:
        logger.debug(f"Mimic: saving to {pickle_file}")
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


def get_unused_recordings() -> list[str]:
    """Get all unused function call recordings.

    Returns a list of unused hash keys.
    """
    global _accessed_hashes
    cache_dir = get_cache_dir()
    if not cache_dir.exists():
        return []

    unused_hashes = []
    for cache_file in cache_dir.iterdir():
        if cache_file.suffix == '.pkl':
            hash_key = cache_file.stem
            if hash_key not in _accessed_hashes:
                unused_hashes.append(hash_key)

    return unused_hashes


def clear_unused_recordings() -> int:
    """Clear all unused function call recordings.

    Returns the number of removed recordings.
    """
    unused_hashes = get_unused_recordings()
    cache_dir = get_cache_dir()

    removed_count = 0
    for hash_key in unused_hashes:
        cache_file = cache_dir / f"{hash_key}.pkl"
        cache_file.unlink(missing_ok=True)
        removed_count += 1

    return removed_count


def _initialize_mimic(config):
    """Initialize the mimic system and return the cache directory path."""
    if config.getini('mimic_vault_path'):
        cache_dir = Path(config.getini('mimic_vault_path'))
        if not cache_dir.is_absolute():
            cache_dir = config.rootpath.absolute() / cache_dir
    else:
        cache_dir = config.rootpath.absolute() / ".mimic_vault"

    set_cache_dir(cache_dir)

    # Add rootpath to path to find
    sys.path.append(str(config.rootpath))
    # Apply mimicking to all functions from ini configuration
    for function_to_mimic in config.getini('mimic_functions'):
        mimic_location(function_to_mimic)


def _import_function_from_string(import_path) -> tuple[object, Callable]:
    """Import a function from an import path string.

    Format: module.submodule:function_name or module.submodule:Class_name.method_name
    """
    try:
        if ':' not in import_path:
            raise ValueError(f"Invalid import path format: {import_path}."
                             f" Expected 'package.module:function'")

        module_path, func_name = import_path.strip().split(':', 1)

        # Import the module
        module = importlib.import_module(module_path)

        path = func_name.split('.')
        return getattr_nested(module, path[:-1]), getattr_nested(module, path)

    except (ImportError, AttributeError, ValueError) as e:
        raise ImportError(f"Failed to import function from '{import_path}'") from e


def getattr_nested(base_obj, path: list[str]):
    if len(path) == 0:
        return base_obj
    else:
        return getattr(getattr_nested(base_obj, path[:-1]), path[-1])
