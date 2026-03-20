"""Simple utility functions for testing pipewright's test-gen workflow."""


def calculate_average(numbers: list[float]) -> float:
    """Calculate the average of a list of numbers."""
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)


def fizzbuzz(n: int) -> str:
    """Return fizz, buzz, fizzbuzz, or the number as string."""
    if n % 15 == 0:
        return "fizzbuzz"
    elif n % 3 == 0:
        return "fizz"
    elif n % 5 == 0:
        return "buzz"
    return str(n)


def reverse_words(sentence: str) -> str:
    """Reverse the order of words in a sentence."""
    return " ".join(sentence.split()[::-1])
