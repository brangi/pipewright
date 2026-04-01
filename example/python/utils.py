# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

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
        return "FizzBuzz"
    elif n % 3 == 0:
        return "Fizz"
    elif n % 5 == 0:
        return "Buzz"
    return str(n)


def reverse_words(sentence: str) -> str:
    """Reverse the order of words in a sentence."""
    return " ".join(sentence.split()[::-1])
