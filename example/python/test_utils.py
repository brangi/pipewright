# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

import pytest
from utils import calculate_average, fizzbuzz, reverse_words


def test_calculate_average_valid_list():
    assert calculate_average([1, 2, 3, 4, 5]) == 3.0

def test_calculate_average_empty_list():
    with pytest.raises(ZeroDivisionError):
        calculate_average([])

def test_calculate_average_negative_numbers():
    assert calculate_average([-1, -2, -3]) == -2.0

def test_fizzbuzz_classic_cases():
    assert fizzbuzz(15) == 'FizzBuzz'
    assert fizzbuzz(3) == 'Fizz'
    assert fizzbuzz(5) == 'Buzz'
    assert fizzbuzz(1) == '1'

def test_fizzbuzz_edge_cases():
    assert fizzbuzz(0) == '0'
    assert fizzbuzz(-3) == '-3'

def test_reverse_words_normal_case():
    assert reverse_words('hello world') == 'world hello'

def test_reverse_words_multiple_spaces():
    assert reverse_words('  hello  world  ') == 'world  hello'

def test_reverse_words_empty_string():
    assert reverse_words('') == ''

def test_reverse_words_single_word():
    assert reverse_words('only') == 'only'