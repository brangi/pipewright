# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

import pytest

from example.python.utils import calculate_average, fizzbuzz, reverse_words


def test_calculate_average():
    # Happy path
    assert calculate_average([1.0, 2.0, 3.0]) == 2.0
    assert calculate_average([10.0, 20.0, 30.0]) == 20.0

    # Edge cases
    assert calculate_average([0.0, 0.0, 0.0]) == 0.0

    # Error handling
    with pytest.raises(ZeroDivisionError):
        calculate_average([])


def test_fizzbuzz():
    # Happy paths
    assert fizzbuzz(3) == 'fizz'
    assert fizzbuzz(5) == 'buzz'
    assert fizzbuzz(15) == 'fizzbuzz'

    # Edge case
    assert fizzbuzz(1) == '1'


def test_reverse_words():
    # Happy path
    assert reverse_words('Hello World') == 'World Hello'
    assert reverse_words('a b c') == 'c b a'

    # Edge cases
    assert reverse_words('') == ''
    assert reverse_words('singleword') == 'singleword'