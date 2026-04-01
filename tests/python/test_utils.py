# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

import pytest
from example.python.utils import calculate_average, fizzbuzz, reverse_words


@pytest.mark.parametrize("numbers, expected", [
    ([1.0, 2.0, 3.0], 2.0),
    ([5.0], 5.0),
    ([0.0, -1.5, 2.5], (0.0 - 1.5 + 2.5) / 3),
])
def test_calculate_average(numbers, expected):
    assert calculate_average(numbers) == pytest.approx(expected)


def test_calculate_average_empty():
    with pytest.raises(ZeroDivisionError):
        calculate_average([])


@pytest.mark.parametrize("n, expected", [
    (15, "FizzBuzz"),
    (3, "Fizz"),
    (5, "Buzz"),
    (2, "2"),
    (0, "FizzBuzz"),
    (-3, "Fizz"),
])
def test_fizzbuzz(n, expected):
    assert fizzbuzz(n) == expected


@pytest.mark.parametrize("input_str, expected", [
    ("hello world", "world hello"),
    ("   a   b   ", "b a"),
    ("", ""),
    ("   ", "  "),
    ("one", "one"),
    ("a b c", "c b a"),
    ("a\tb\t\tc", "c b a"),
])
def test_reverse_words(input_str, expected):
    assert reverse_words(input_str) == expected