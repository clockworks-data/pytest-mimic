def test_mimic_across_runs(pytester):
    pytester.makeini("""
        [pytest]
        asyncio_default_fixture_loop_scope = "session"
    """)
    pytester.makeconftest(
        """
        from src.pytest_mimic.plugin import _mimic_all_functions

        def pytest_configure(config):
            _mimic_all_functions(config)

    """
    )
    pytester.makepyfile(
        """
        import pytest
        import os
        from src.pytest_mimic.mimic_manager import mimic

        async def async_func_to_mimic(a,b):
            return {"result": a+b}

        def sync_func_to_mimic(a,b):
            return {"result": a+b}

        @pytest.mark.asyncio
        async def test_mimic_async_func():
            mimic(async_func_to_mimic)

            result = await async_func_to_mimic(5, b=3)

            assert result['result'] == 8

        def test_mimic_sync_func():
            mimic(sync_func_to_mimic)

            result = sync_func_to_mimic(5, b=3)

            assert result['result'] == 8
        """
    )
    results = pytester.runpytest('-v')

    # Both tests should fail since we don't have recordings yet
    assert results.parseoutcomes()['failed'] == 2
    assert "RuntimeError: Missing mim" in '\n'.join(results.outlines)

    # now run with record mode on
    results = pytester.runpytest('--mimic-record', '-v')

    # Both tests should pass when recording
    assert results.parseoutcomes()['passed'] == 2

    # now run with record mode off again, using stored input-output
    results = pytester.runpytest('-v')

    # Both tests should pass with replay
    assert results.parseoutcomes()['passed'] == 2


