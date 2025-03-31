
def test_mimic_across_runs(pytester):
    pytester.makeconftest(
        """
        import pytest
        
        from src.pytest_mimic.mimic_manager import MimicManager
        
        def pytest_configure(config):
            MimicManager.initialize(config)

    """
    )
    pytester.makepyfile(
        """
        import pytest
        import os
        from src.pytest_mimic.mimic_manager import mimic_function_call
        
        async def func_to_mimic(a,b):
            return {"result": a+b}
        
        @pytest.mark.asyncio
        async def test_mimic_func():
            mimic_function_call(func_to_mimic)
            
            result = await func_to_mimic(5, b=3)
            
            assert result['result'] == 8
        """
    )
    results = pytester.runpytest('-v')

    assert results.parseoutcomes()['failed'] == 1
    assert "RuntimeError: Missing mim" in results.outlines[-2]

    # now run with record mode on
    results = pytester.runpytest('--mimic-record', '-v')

    assert results.parseoutcomes()['passed'] == 1

    # now run with record mode off again, using stored input-output
    results = pytester.runpytest('--mimic-record', '-v')

    assert results.parseoutcomes()['passed'] == 1
