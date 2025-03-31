

async def example_function_to_mimic(a, b):
    return a+b


async def example_function_that_calls_function_to_mimic(a,b):
    return (await example_function_to_mimic(a, b)) + (await example_function_to_mimic(a, b))
