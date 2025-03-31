

async def example_function_to_mimic(a, b):
    return a+b


async def example_function_that_calls_function_to_mimic(a,b):
    return (await example_function_to_mimic(a, b)) + (await example_function_to_mimic(a, b))


def sync_example_function_to_mimic(a, b):
    return a+b


def sync_example_function_that_calls_function_to_mimic(a,b):
    return sync_example_function_to_mimic(a, b) + sync_example_function_to_mimic(a, b)
