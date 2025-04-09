

async def example_function_to_mimic(a, b):
    return a+b


async def example_function_that_calls_function_to_mimic(a,b):
    return (await example_function_to_mimic(a, b)) + (await example_function_to_mimic(a, b))


def sync_example_function_to_mimic(a, b):
    return a+b


def sync_example_function_that_calls_function_to_mimic(a,b):
    return sync_example_function_to_mimic(a, b) + sync_example_function_to_mimic(a, b)


class ExampleClass:
    def __init__(self):
        self.instance_value = 0

    @classmethod
    def example_classmethod(cls, a, b):
        return a+b

    @staticmethod
    def example_staticmethod(a, b):
        return a+b

    def example_method(self, a, b):
        return self.instance_value+a+b

    def example_mutable_method(self, a, b):
        self.instance_value = self.instance_value + 1
        return self.instance_value + a + b

    class NestedClass:
        class DoubleNestedClass:
            def __init__(self):
                self.instance_value = 0

            @classmethod
            def example_dnested_class(cls, a, b):
                return a + b

            @staticmethod
            def example_dnested_staticmethod(a, b):
                return a + b

            def example_dnested_method(self, a, b):
                return self.instance_value + a + b
