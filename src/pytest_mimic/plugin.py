import inspect
import importlib.util
import os
import sys
import warnings
from pathlib import Path

from .mimic_manager import MimicManager


def pytest_addoption(parser):
    group = parser.getgroup('mimic')
    group.addoption(
        '--mimic-record',
        action='store_true',
        default=False,
        help='Record function calls during tests and save them for future replay'
    )
    
    parser.addini(
        'mimic_functions',
        type='linelist',
        help='List of functions to mimic (in format: module.submodule:function_name)',
        default=[]
    )


def _import_function_from_string(import_path, pytest_config_root_path):
    """Import a function from an import path string.
    
    Format: module.submodule:function_name
    Example: tests.example_module:example_function_to_mimic
    """
    try:
        if ':' not in import_path:
            raise ValueError(f"Invalid import path format: {import_path}. Expected 'module:function'")
            
        module_path, func_name = import_path.strip().split(':', 1)

        sys.path.append(str(pytest_config_root_path))

        # Import the module
        module = importlib.import_module(module_path)
        
        # Get the function from the module
        if not hasattr(module, func_name):
            raise ValueError(f"Function '{func_name}' not found in module '{module_path}'")
            
        return getattr(module, func_name)

    except (ImportError, AttributeError, ValueError) as e:
        warnings.warn(f"Failed to import function from '{import_path}': {e}")
        return None


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


def pytest_configure(config):
    """Configure pytest based on command-line options."""
    if config.getoption("--mimic-record"):
        os.environ["RECORD_FUNC_CALLS"] = "1"
    else:
        if "RECORD_FUNC_CALLS" not in os.environ:
            # Ensure it's set to 0 if not explicitly enabled
            os.environ["RECORD_FUNC_CALLS"] = "0"

    _mimic_all_functions(config)


def _mimic_all_functions(config):
    # Initialize the MockFuncCallManager singleton
    manager = MimicManager.initialize(config)
    # Apply mimicking to all functions from conftest.py
    functions_to_mimic = _get_functions_to_mimic(config)
    print(f"Mimicking: {functions_to_mimic}")
    for func in functions_to_mimic:
        manager.mimic(func)
