import asyncio
import contextlib
import hashlib
import importlib
import inspect
import logging
import os
import pickle
import pkgutil
import sys
import warnings
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Optional

logger = logging.getLogger("pytest_mimic")

_cache_dir: Optional[Path] = None
_accessed_hashes: set = set()


def set_cache_dir(path: Path):
    """Set the directory path where mimic recordings will be stored.

    Args:
        path: Path object pointing to the mimic vault directory
    """
    global _cache_dir
    _cache_dir = path


def get_cache_dir() -> Path:
    """Get the mimic cache directory path.

    Returns:
        The Path object pointing to the mimic vault directory

    Raises:
        RuntimeError: If the mimic system has not been initialized
    """
    if _cache_dir is None:
        raise RuntimeError("Mimic functionality not initialized. Initialize first.")
    return _cache_dir


def try_load_result_from_cache(func, args, kwargs) -> tuple[Optional[object], Optional[str]]:
    """Try to load a recorded function call result from the mimic vault.

    This function attempts to retrieve a previously recorded function call result.
    If the function call has not been recorded and we're in record mode, it returns
    the hash key to allow later storage of the result.

    Args:
        func: The function being called
        args: Positional arguments to the function
        kwargs: Keyword arguments to the function

    Returns:
        A tuple containing:
        - The recorded result (or None if not found/in record mode)
        - The hash key (only if in record mode and result not found, otherwise None)

    Raises:
        RuntimeError: If the result is not found and we're not in record mode
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
        raise RuntimeError(
            f"Missing mimic-recorded result for function call "
            f"{func.__name__} with hash {hash_key}.\n"
            f"Run pytest with --mimic-record to record responses."
        )
    return None, hash_key


@contextlib.contextmanager
def mimic(target: str, classmethod_warning: bool = True):
    """Context manager that intercepts calls to a function and records or replays its behavior.

    Args:
        target: The import path of function or method to mimic, in the format
                    "module.submodule.function_name"
                        or
                    "module.submodule.Class.method_name"
        classmethod_warning: Whether to issue a warning when mimicking classmethods
            that might mutate class state (default: True)

    Yields:
        None: This context manager doesn't yield a value

    Raises:
        ValueError: If attempting to mimic a method bound to an instance

    Examples:
        >>> with mimic(expensive_function):
        ...     result = function_that_calls_expensive_function()

        >>> # Mimicking a class method
        >>> with mimic(MyClass.class_method):
        ...     result = function_that_calls_class_method()
    """

    parent_obj, func = _mimic(target, classmethod_warning)
    yield
    setattr(parent_obj, func.__name__, func)


def _mimic(target, classmethod_warning: bool = True):
    """Replace a function or method with a version that records or replays its behavior.

    This is an internal function used by both mimic() and _initialize_mimic().
    It handles both synchronous and asynchronous functions.

    Args:
        target: A string in the format "module.submodule.function_name" or
                     "module.submodule.Class.method_name"
    """
    parent_obj, func = _import_function_from_string(target, classmethod_warning)
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
                    raise RuntimeError(
                        f"Running function {func} has mutated its inputs.\n"
                        f"Mimicking shouldn't be used on functions or methods"
                        f" that mutate its input (or parent object)"
                    )

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
                    raise RuntimeError(
                        f"Running function {func} has mutated its inputs.\n"
                        f"Mimicking shouldn't be used on functions or methods"
                        f" that mutate its input (or parent object)"
                    )

                # Save the result for future use
                save_func_result(hash_key, result)

            return result

        setattr(parent_obj, func.__name__, sync_wrapper)

    return parent_obj, func


def compute_hash(func: Callable, args: tuple, kwargs: dict) -> str:
    """Compute a deterministic hash for a function call.

    This function creates a unique hash based on the function identity and its inputs.
    The hash is used as a key to store and retrieve recorded function results.

    Args:
        func: The function being called
        args: Positional arguments to the function
        kwargs: Keyword arguments to the function

    Returns:
        A hex digest string that uniquely identifies this function call
    """
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
    logger.debug(
        f"Mimic: function {func.__name__} with inputs {args} and {kwargs} generated hash {hash_key}"
    )

    return hash_key


def save_func_result(hash_key: str, result: Any) -> None:
    """Save a function call result to the mimic vault.

    Args:
        hash_key: The unique hash key for this function call
        result: The result of the function call to save
    """
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
    """Get the path to the pickle file for a specific function call.

    Args:
        hash_key: The unique hash key for the function call

    Returns:
        A Path object pointing to the pickle file location
    """
    return get_cache_dir() / f"{hash_key}.pkl"


def get_unused_recordings() -> list[str]:
    """Get all unused function call recordings.

    This function identifies all recorded function calls that weren't accessed
    during the current test run. These may be obsolete recordings that are no
    longer needed.

    Returns:
        A list of hash keys corresponding to unused recordings
    """
    global _accessed_hashes
    cache_dir = get_cache_dir()
    if not cache_dir.exists():
        return []

    unused_hashes = []
    for cache_file in cache_dir.iterdir():
        if cache_file.suffix == ".pkl":
            hash_key = cache_file.stem
            if hash_key not in _accessed_hashes:
                unused_hashes.append(hash_key)

    return unused_hashes


def clear_unused_recordings() -> int:
    """Clear all unused function call recordings.

    This function deletes all recorded function calls that weren't accessed
    during the current test run. This helps keep the mimic vault size manageable
    by removing obsolete recordings.

    Returns:
        The number of removed recordings
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
    """Initialize the mimic system and configure the mimic vault path.

    This function is called during pytest startup. It sets up the vault directory
    and applies mimicking to all functions specified in the configuration.

    Args:
        config: The pytest configuration object
    """
    if config.getini("mimic_vault_path"):
        cache_dir = Path(config.getini("mimic_vault_path"))
        if not cache_dir.is_absolute():
            cache_dir = config.rootpath.absolute() / cache_dir
    else:
        cache_dir = config.rootpath.absolute() / ".mimic_vault"

    set_cache_dir(cache_dir)

    # Add rootpath to path to find
    sys.path.append(str(config.rootpath))
    # Apply mimicking to all functions from ini configuration
    for function_to_mimic in config.getini("mimic_functions"):
        _mimic(function_to_mimic)


def _import_function_from_string(import_path, classmethod_warning: bool) -> tuple[object, Callable]:
    """Import a function and its parent from an import path string.

    Args:
        import_path: A string in the format "module.submodule.function_name" or
                     "module.submodule.Class.method_name"

    Returns:
        A tuple containing:
        - The parent object (module or class) that contains the function
        - The function or method object

    Raises:
        ImportError: If the function cannot be imported from the given path
        ValueError: If the import path format is invalid
    """
    try:
        callable_to_mimic = pkgutil.resolve_name(import_path)

        if inspect.isclass(callable_to_mimic):
            raise ValueError(
                f"\nAttempting to mimic class {import_path}."
                f"\npytest-mimic cannot mimic classes. Mimic its method(s) instead"
            )

        if len(callable_to_mimic.__qualname__.split(".")) == 1:
            # callable is module-level function
            return importlib.import_module(callable_to_mimic.__module__), callable_to_mimic

        if inspect.ismethod(callable_to_mimic):
            if classmethod_warning:
                warnings.warn(
                    f"\nMimicking classmethod {import_path}.\n"
                    f"Mimicking cannot check for class-level mutations caused"
                    f" by calling this method.\n"
                    f"If you're sure that this classmethod does not mutate its class"
                    f" you can use\n"
                    f"\tmimic(<your_classmethod>, classmethod_warning=False)\n"
                    f"to suppress this warning.",
                    stacklevel=2,
                )

        parent = pkgutil.resolve_name(
            callable_to_mimic.__module__ + "." + callable_to_mimic.__qualname__.rsplit(".", 1)[0]
        )

        return parent, callable_to_mimic

    except (ImportError, AttributeError, ValueError, TypeError) as e:
        raise ImportError(f"Failed to import function from path '{import_path}'") from e
