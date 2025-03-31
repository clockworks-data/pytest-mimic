import os

import pytest

from tests.example_module import example_function_to_mimic


@pytest.mark.asyncio
async def test_mimicking_at_global_level():
    os.environ["RECORD_FUNC_CALLS"] = "0"
    with pytest.raises(RuntimeError):
        await example_function_to_mimic(1, 2)

    os.environ["RECORD_FUNC_CALLS"] = "1"
    res_recording = await example_function_to_mimic(1, 2)

    os.environ["RECORD_FUNC_CALLS"] = "0"

    res_mimicked = await example_function_to_mimic(1, 2)

    assert res_recording == res_mimicked
