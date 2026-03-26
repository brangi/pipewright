# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

"""Comprehensive tests for example/utils.py utility functions."""

import math
import pytest
from example.python.utils import calculate_average, fizzbuzz, reverse_words


class TestCalculateAverage:
    """Test suite for calculate_average function."""

    # Happy path tests
    def test_calculate_average_simple_positive_numbers(self):
        """Test average calculation with simple positive numbers."""
        assert calculate_average([2.0, 4.0, 6.0]) == 4.0

    def test_calculate_average_single_number(self):
        """Test average of a single number returns itself."""
        assert calculate_average([5.0]) == 5.0

    def test_calculate_average_two_numbers(self):
        """Test average calculation with two numbers."""
        assert calculate_average([1.0, 3.0]) == 2.0

    def test_calculate_average_many_numbers(self):
        """Test average calculation with many numbers."""
        numbers = [i for i in range(1, 101)]  # 1 to 100
        expected = sum(numbers) / len(numbers)
        assert calculate_average([float(n) for n in numbers]) == expected

    def test_calculate_average_negative_numbers(self):
        """Test average calculation with negative numbers."""
        assert calculate_average([-1.0, -3.0, -5.0]) == -3.0

    def test_calculate_average_mixed_positive_negative(self):
        """Test average calculation with mixed positive and negative numbers."""
        assert calculate_average([-5.0, 0.0, 5.0]) == 0.0

    def test_calculate_average_zero(self):
        """Test average calculation when all numbers are zero."""
        assert calculate_average([0.0, 0.0, 0.0]) == 0.0

    def test_calculate_average_contains_zero(self):
        """Test average calculation with a zero in the list."""
        assert calculate_average([0.0, 2.0, 4.0]) == 2.0

    def test_calculate_average_fractional_numbers(self):
        """Test average calculation with fractional numbers."""
        result = calculate_average([1.5, 2.5, 3.5])
        assert result == 2.5

    def test_calculate_average_large_numbers(self):
        """Test average calculation with large numbers."""
        assert calculate_average([1e6, 2e6, 3e6]) == 2e6

    def test_calculate_average_small_fractional_numbers(self):
        """Test average calculation with small fractional numbers."""
        result = calculate_average([0.1, 0.2, 0.3])
        assert abs(result - 0.2) < 1e-9

    def test_calculate_average_returns_float(self):
        """Test that calculate_average returns a float."""
        result = calculate_average([1.0, 2.0, 3.0])
        assert isinstance(result, float)

    # Edge cases
    def test_calculate_average_very_large_list(self):
        """Test average calculation with a very large list."""
        large_list = [float(i) for i in range(10000)]
        expected = 4999.5  # Average of 0 to 9999
        assert calculate_average(large_list) == expected

    def test_calculate_average_precision_with_floats(self):
        """Test that floating point precision is maintained."""
        numbers = [0.1, 0.2, 0.3]
        result = calculate_average(numbers)
        assert math.isclose(result, 0.2, rel_tol=1e-9)

    def test_calculate_average_alternating_values(self):
        """Test average with alternating high and low values."""
        assert calculate_average([1.0, 100.0, 1.0, 100.0]) == 50.5

    # Error handling tests
    def test_calculate_average_empty_list_raises_error(self):
        """Test that empty list raises ZeroDivisionError."""
        with pytest.raises(ZeroDivisionError):
            calculate_average([])

    def test_calculate_average_with_integers(self):
        """Test that function works with integers (converts to float division)."""
        # Python 3 division always returns float
        result = calculate_average([1, 2, 3])
        assert result == 2.0

    def test_calculate_average_none_in_list(self):
        """Test behavior when None is in the list."""
        with pytest.raises(TypeError):
            calculate_average([1.0, None, 3.0])

    def test_calculate_average_string_in_list(self):
        """Test behavior when string is in the list."""
        with pytest.raises(TypeError):
            calculate_average([1.0, "2.0", 3.0])


class TestFizzbuzz:
    """Test suite for fizzbuzz function."""

    # Happy path tests - FizzBuzz numbers
    def test_fizzbuzz_divisible_by_15(self):
        """Test numbers divisible by 15 return 'fizzbuzz'."""
        assert fizzbuzz(15) == "fizzbuzz"
        assert fizzbuzz(30) == "fizzbuzz"
        assert fizzbuzz(45) == "fizzbuzz"

    def test_fizzbuzz_divisible_by_3_only(self):
        """Test numbers divisible by 3 (but not 15) return 'fizz'."""
        assert fizzbuzz(3) == "fizz"
        assert fizzbuzz(6) == "fizz"
        assert fizzbuzz(9) == "fizz"
        assert fizzbuzz(12) == "fizz"
        assert fizzbuzz(18) == "fizz"

    def test_fizzbuzz_divisible_by_5_only(self):
        """Test numbers divisible by 5 (but not 15) return 'buzz'."""
        assert fizzbuzz(5) == "buzz"
        assert fizzbuzz(10) == "buzz"
        assert fizzbuzz(20) == "buzz"
        assert fizzbuzz(25) == "buzz"

    def test_fizzbuzz_not_divisible_by_3_or_5(self):
        """Test numbers not divisible by 3 or 5 return string of number."""
        assert fizzbuzz(1) == "1"
        assert fizzbuzz(2) == "2"
        assert fizzbuzz(4) == "4"
        assert fizzbuzz(7) == "7"
        assert fizzbuzz(8) == "8"
        assert fizzbuzz(11) == "11"

    def test_fizzbuzz_zero(self):
        """Test zero returns 'fizzbuzz' (divisible by both 3 and 5)."""
        assert fizzbuzz(0) == "fizzbuzz"

    def test_fizzbuzz_one(self):
        """Test one returns '1'."""
        assert fizzbuzz(1) == "1"

    def test_fizzbuzz_large_fizzbuzz_number(self):
        """Test large numbers divisible by 15."""
        assert fizzbuzz(300) == "fizzbuzz"
        assert fizzbuzz(999) == "fizz"
        assert fizzbuzz(1000) == "buzz"

    # Edge cases
    def test_fizzbuzz_negative_fizzbuzz(self):
        """Test negative numbers divisible by 15."""
        assert fizzbuzz(-15) == "fizzbuzz"
        assert fizzbuzz(-30) == "fizzbuzz"

    def test_fizzbuzz_negative_fizz(self):
        """Test negative numbers divisible by 3."""
        assert fizzbuzz(-3) == "fizz"
        assert fizzbuzz(-9) == "fizz"

    def test_fizzbuzz_negative_buzz(self):
        """Test negative numbers divisible by 5."""
        assert fizzbuzz(-5) == "buzz"
        assert fizzbuzz(-10) == "buzz"

    def test_fizzbuzz_negative_regular_number(self):
        """Test negative numbers not divisible by 3 or 5."""
        assert fizzbuzz(-1) == "-1"
        assert fizzbuzz(-7) == "-7"

    def test_fizzbuzz_negative_one(self):
        """Test negative one."""
        assert fizzbuzz(-1) == "-1"

    def test_fizzbuzz_large_numbers(self):
        """Test fizzbuzz with very large numbers."""
        assert fizzbuzz(999999) == "fizz"  # divisible by 3
        assert fizzbuzz(1000000) == "buzz"  # divisible by 5
        assert fizzbuzz(1000005) == "fizzbuzz"  # divisible by 15

    # Return type tests
    def test_fizzbuzz_returns_string(self):
        """Test that fizzbuzz always returns a string."""
        assert isinstance(fizzbuzz(1), str)
        assert isinstance(fizzbuzz(3), str)
        assert isinstance(fizzbuzz(5), str)
        assert isinstance(fizzbuzz(15), str)

    def test_fizzbuzz_consistent_output(self):
        """Test that same input always produces same output."""
        assert fizzbuzz(15) == fizzbuzz(15)
        assert fizzbuzz(3) == fizzbuzz(3)
        assert fizzbuzz(7) == fizzbuzz(7)

    # Boundary tests
    def test_fizzbuzz_sequence_1_to_15(self):
        """Test fizzbuzz for the classic sequence 1-15."""
        expected = [
            "1", "2", "fizz", "4", "buzz", "fizz", "7", "8", "fizz",
            "buzz", "11", "fizz", "13", "14", "fizzbuzz"
        ]
        for i in range(1, 16):
            assert fizzbuzz(i) == expected[i - 1]

    def test_fizzbuzz_divisibility_precedence(self):
        """Test that 15 divisibility is checked first (returns fizzbuzz, not just fizz or buzz)."""
        # 15 should return 'fizzbuzz', not just 'fizz' (first match)
        assert fizzbuzz(15) == "fizzbuzz"
        assert fizzbuzz(15) != "fizz"
        assert fizzbuzz(15) != "buzz"


class TestReverseWords:
    """Test suite for reverse_words function."""

    # Happy path tests
    def test_reverse_words_simple_sentence(self):
        """Test reversing a simple sentence."""
        assert reverse_words("hello world") == "world hello"

    def test_reverse_words_three_words(self):
        """Test reversing a sentence with three words."""
        assert reverse_words("one two three") == "three two one"

    def test_reverse_words_single_word(self):
        """Test that a single word returns itself."""
        assert reverse_words("hello") == "hello"

    def test_reverse_words_multiple_spaces(self):
        """Test that multiple spaces are normalized to single space."""
        result = reverse_words("hello  world")
        # split() removes all whitespace and rejoins with single space
        assert result == "world hello"

    def test_reverse_words_leading_trailing_spaces(self):
        """Test that leading/trailing spaces are handled correctly."""
        assert reverse_words("  hello world  ") == "world hello"

    def test_reverse_words_tabs_and_spaces(self):
        """Test that tabs and multiple spaces are normalized."""
        result = reverse_words("hello\tworld")
        assert result == "world hello"

    def test_reverse_words_long_sentence(self):
        """Test reversing a longer sentence."""
        assert reverse_words("the quick brown fox jumps") == "jumps fox brown quick the"

    def test_reverse_words_with_punctuation(self):
        """Test reversing words with punctuation attached."""
        # Note: punctuation stays with the word
        assert reverse_words("hello, world!") == "world! hello,"

    def test_reverse_words_numbers(self):
        """Test reversing a sentence with numbers."""
        assert reverse_words("one 2 three 4") == "4 three 2 one"

    # Edge cases
    def test_reverse_words_empty_string(self):
        """Test reversing an empty string."""
        assert reverse_words("") == ""

    def test_reverse_words_only_spaces(self):
        """Test reversing a string with only spaces."""
        assert reverse_words("   ") == ""

    def test_reverse_words_single_space(self):
        """Test reversing a single space."""
        assert reverse_words(" ") == ""

    def test_reverse_words_two_words_with_spaces(self):
        """Test reversing two words with various spacing."""
        assert reverse_words("  one   two  ") == "two one"

    def test_reverse_words_newline_characters(self):
        """Test that newline characters are treated as whitespace."""
        result = reverse_words("hello\nworld")
        assert result == "world hello"

    def test_reverse_words_mixed_whitespace(self):
        """Test that mixed whitespace types are normalized."""
        result = reverse_words("hello  \t  world  \n  test")
        assert result == "test world hello"

    def test_reverse_words_unicode_characters(self):
        """Test reversing words with unicode characters."""
        assert reverse_words("café naïve") == "naïve café"

    def test_reverse_words_special_characters(self):
        """Test reversing words with special characters."""
        assert reverse_words("@user #hashtag") == "#hashtag @user"

    def test_reverse_words_hyphenated_words(self):
        """Test that hyphenated words are treated as single words."""
        assert reverse_words("mother-in-law is here") == "here is mother-in-law"

    def test_reverse_words_apostrophes(self):
        """Test words with apostrophes."""
        assert reverse_words("don't you see") == "see you don't"

    def test_reverse_words_very_long_sentence(self):
        """Test reversing a very long sentence."""
        long_sentence = " ".join([f"word{i}" for i in range(100)])
        result = reverse_words(long_sentence)
        expected_words = [f"word{i}" for i in range(99, -1, -1)]
        assert result == " ".join(expected_words)

    # Return type tests
    def test_reverse_words_returns_string(self):
        """Test that reverse_words always returns a string."""
        assert isinstance(reverse_words("hello world"), str)
        assert isinstance(reverse_words("test"), str)
        assert isinstance(reverse_words(""), str)

    def test_reverse_words_is_reversible(self):
        """Test that reversing twice returns the original."""
        original = "hello world test"
        reversed_once = reverse_words(original)
        reversed_twice = reverse_words(reversed_once)
        assert reversed_twice == original

    # Case sensitivity tests
    def test_reverse_words_preserves_case(self):
        """Test that case is preserved during reversal."""
        assert reverse_words("Hello World") == "World Hello"
        assert reverse_words("UPPER lower") == "lower UPPER"

    # Consistency tests
    def test_reverse_words_consistent_output(self):
        """Test that same input always produces same output."""
        assert reverse_words("hello world") == reverse_words("hello world")

    def test_reverse_words_order_matters(self):
        """Test that actual word order is reversed."""
        result = reverse_words("first second third")
        assert result.split()[0] == "third"
        assert result.split()[1] == "second"
        assert result.split()[2] == "first"
