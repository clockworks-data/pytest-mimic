import logging
import os

from src.pytest_mimic.mimic_manager import _mimic_all_functions

logger = logging.getLogger("pytest_mimic")


def pytest_addoption(parser):
    group = parser.getgroup('mimic')
    group.addoption(
        '--mimic-record',
        action='store_true',
        default=False,
        help='Record function calls during tests and save them for future replay'
    )
    group.addoption(
        '--mimic-clear-unused',
        action='store_true',
        default=False,
        help='Clear unused mimic recordings after test run'
    )
    group.addoption(
        '--mimic-fail-on-unused',
        action='store_true',
        default=False,
        help='Fail the test run if any mimic recordings were not used'
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

    if config.getoption("--mimic-clear-unused"):
        os.environ["MIMIC_CLEAR_UNUSED"] = "1"
    else:
        os.environ["MIMIC_CLEAR_UNUSED"] = "0"

    if config.getoption("--mimic-fail-on-unused"):
        os.environ["MIMIC_FAIL_ON_UNUSED"] = "1"
    else:
        os.environ["MIMIC_FAIL_ON_UNUSED"] = "0"

    _mimic_all_functions(config)


def pytest_unconfigure(config):
    """Clean up after all tests have run."""
    from src.pytest_mimic.mimic_manager import get_unused_recordings

    unused_recordings = get_unused_recordings()
    unused_count = len(unused_recordings)

    if os.environ.get("MIMIC_CLEAR_UNUSED", "0") == "1" and unused_count > 0:
        from src.pytest_mimic.mimic_manager import clear_unused_recordings
        removed_count = clear_unused_recordings()
        logger.info(f"Removed {removed_count} unused mimic recordings")

    if os.environ.get("MIMIC_FAIL_ON_UNUSED", "0") == "1" and unused_count > 0:
        # Limit the number of hashes to display to avoid overwhelming output
        display_hashes = unused_recordings[:10]
        additional = ""
        if unused_count > 10:
            additional = f" and {unused_count - 10} more"

        raise RuntimeError(f"Found {unused_count} unused mimic recordings.\n"
                           f"Unused hashes: {', '.join(display_hashes)}{additional}\n"
                           f"Use --mimic-clear-unused to remove them"
                           f" or fix your tests to use them.")
