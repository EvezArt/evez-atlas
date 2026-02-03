import math


def add(a, b):
    return a + b


def square(x):
    return math.pow(x, 2)


class Greeter:
    def greet(self, name: str) -> str:
        return f"Hello {name}"
