import os

import pytest

from tests.example_module import example_function_to_mimic


@pytest.mark.asyncio
async def test_mimicking_at_global_level():
    os.environ["MIMIC_RECORD"] = "0"
    with pytest.raises(RuntimeError):
        # this function should be mimicked from the pyproject.toml
        await example_function_to_mimic(1, 2)

    os.environ["MIMIC_RECORD"] = "1"
    res_recording = await example_function_to_mimic(1, 2)

    os.environ["MIMIC_RECORD"] = "0"

    res_mimicked = await example_function_to_mimic(1, 2)

    assert res_recording == res_mimicked
