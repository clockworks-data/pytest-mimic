import os

from src.pytest_mimic.mimic_manager import _mimic_all_functions


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

    parser.addini(
        'mimic_vault_path',
        help='Directory to store cached function call results',
        default='.mimic_vault'
    )


def pytest_configure(config):
    """Configure pytest based on command-line options."""
    if config.getoption("--mimic-record"):
        os.environ["MIMIC_RECORD"] = "1"
    else:
        if "MIMIC_RECORD" not in os.environ:
            # Ensure it's set to 0 if not explicitly enabled
            os.environ["MIMIC_RECORD"] = "0"

    _mimic_all_functions(config)

