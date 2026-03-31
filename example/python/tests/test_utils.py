# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

"""Comprehensive tests for example.python.utils module."""

import pytest
from example.python.utils import calculate_average, fizzbuzz, reverse_words


class TestCalculateAverage:
    """Tests for calculate_average function."""

    def test_happy_path_integers(self):
        """Test with typical integer values."""
        assert calculate_average([1, 2, 3]) == 2.0
        assert calculate_average([10, 20, 30, 40]) == 25.0

    def test_happy_path_floats(self):
        """Test with float values including decimals."""
        assert calculate_average([1.5, 2.5, 3.5]) == 2.5
        assert calculate_average([0.1, 0.2, 0.3]) == pytest.approx(0.2)

    def test_single_element(self):
        """Test with a single element list."""
        assert calculate_average([42.0]) == 42.0
        assert calculate_average([-5]) == -5.0

    def test_negative_numbers(self):
        """Test with negative numbers."""
        assert calculate_average([-1, -2, -3]) == -2.0
        assert calculate_average([-10, 10]) == 0.0
        assert calculate_average([-5.5, 5.5]) == 0.0

    def test_all_zeros(self):
        """Test with all zeros."""
        assert calculate_average([0.0, 0.0, 0.0]) == 0.0

    def test_large_numbers(self):
        """Test with very large numbers."""
        large = 1e200
        assert calculate_average([large, large]) == large

    def test_very_small_numbers(self):
        """Test with very small numbers."""
        small = 1e-308
        assert calculate_average([small, small]) == small

    def test_mixed_sign_floats(self):
        """Test with mixed positive and negative floats."""
        assert calculate_average([1.5, -1.5, 2.0]) == pytest.approx(0.6666666667)

    def test_empty_list_raises_zero_division(self):
        """Test that empty list raises ZeroDivisionError."""
        with pytest.raises(ZeroDivisionError):
            calculate_average([])

    def test_precision(self):
        """Test floating point precision."""
        result = calculate_average([0.1, 0.2, 0.3])
        # Using pytest.approx for floating point comparison
        assert result == pytest.approx(0.2, abs=1e-10)


class TestFizzbuzz:
    """Tests for fizzbuzz function."""

    def test_multiples_of_three(self):
        """Test numbers divisible by 3 but not 5."""
        assert fizzbuzz(3) == "fizz"
        assert fizzbuzz(6) == "fizz"
        assert fizzbuzz(9) == "fizz"
        assert fizzbuzz(99) == "fizz"

    def test_multiples_of_five(self):
        """Test numbers divisible by 5 but not 3."""
        assert fizzbuzz(5) == "buzz"
        assert fizzbuzz(10) == "buzz"
        assert fizzbuzz(20) == "buzz"
        assert fizzbuzz(100) == "buzz"

    def test_multiples_of_fifteen(self):
        """Test numbers divisible by both 3 and 5."""
        assert fizzbuzz(15) == "fizzbuzz"
        assert fizzbuzz(30) == "fizzbuzz"
        assert fizzbuzz(45) == "fizzbuzz"
        assert fizzbuzz(150) == "fizzbuzz"

    def test_non_multiples(self):
        """Test numbers not divisible by 3 or 5."""
        assert fizzbuzz(1) == "1"
        assert fizzbuzz(2) == "2"
        assert fizzbuzz(4) == "4"
        assert fizzbuzz(7) == "7"
        assert fizzbuzz(8) == "8"
        assert fizzbuzz(11) == "11"

    def test_zero(self):
        """Test zero - edge case."""
        assert fizzbuzz(0) == "fizzbuzz"  # 0 is divisible by any number

    def test_negative_numbers(self):
        """Test negative numbers."""
        assert fizzbuzz(-3) == "fizz"
        assert fizzbuzz(-5) == "buzz"
        assert fizzbuzz(-15) == "fizzbuzz"
        assert fizzbuzz(-1) == "-1"
        assert fizzbuzz(-2) == "-2"

    def test_large_numbers(self):
        """Test very large numbers."""
        assert fizzbuzz(300) == "fizzbuzz"  # 300 = 15 * 20
        assert fizzbuzz(303) == "fizz"
        assert fizzbuzz(305) == "buzz"
        assert fizzbuzz(307) == "307"

    def test_boundary_cases(self):
        """Test boundary values around multiples."""
        assert fizzbuzz(14) == "14"
        assert fizzbuzz(16) == "16"
        assert fizzbuzz(29) == "29"
        assert fizzbuzz(31) == "31"


class TestReverseWords:
    """Tests for reverse_words function."""

    def test_two_words(self):
        """Test simple two-word reversal."""
        assert reverse_words("Hello World") == "World Hello"
        assert reverse_words("foo bar") == "bar foo"

    def test_multiple_words(self):
        """Test reversal of multiple words."""
        assert reverse_words("one two three four") == "four three two one"
        assert reverse_words("a b c d e") == "e d c b a"

    def test_single_word(self):
        """Test single word returns same word."""
        assert reverse_words("single") == "single"
        assert reverse_words("word") == "word"

    def test_empty_string(self):
        """Test empty string returns empty string."""
        assert reverse_words("") == ""

    def test_whitespace_only(self):
        """Test string with only whitespace."""
        assert reverse_words("   ") == ""
        assert reverse_words("\t\n") == ""

    def test_leading_trailing_spaces(self):
        """Test leading and trailing spaces are removed."""
        assert reverse_words("  Hello World  ") == "World Hello"
        assert reverse_words("  single  ") == "single"

    def test_multiple_spaces_between_words(self):
        """Test multiple spaces between words are collapsed."""
        assert reverse_words("Hello   World") == "World Hello"
        assert reverse_words("a    b    c") == "c b a"

    def test_mixed_whitespace(self):
        """Test tabs and newlines are handled."""
        assert reverse_words("Hello\tWorld") == "World Hello"
        assert reverse_words("Line1\nLine2") == "Line2 Line1"

    def test_unicode_characters(self):
        """Test unicode and non-ASCII characters."""
        assert reverse_words("café au lait") == "lait au café"
        assert reverse_words("日本語 テスト") == "テスト 日本語"
        assert reverse_words("🎉 🎊 party") == "party 🎊 🎉"

    def test_mixed_case(self):
        """Test case preservation."""
        assert reverse_words("Hello World") == "World Hello"
        assert reverse_words("UPPER lower") == "lower UPPER"
        assert reverse_words("Mixed Case Words") == "Words Case Mixed"

    def test_numbers_as_words(self):
        """Test numbers treated as words."""
        assert reverse_words("1 2 3") == "3 2 1"
        assert reverse_words("10 20 30 40") == "40 30 20 10"

    def test_punctuation(self):
        """Test punctuation is preserved as part of words."""
        assert reverse_words("Hello, World!") == "World! Hello,"
        assert reverse_words("end.") == "end."

    def test_trailing_space_handling(self):
        """Ensure no trailing or leading spaces in output."""
        result = reverse_words("  many   spaces   here  ")
        assert result == "here spaces many"
        assert not result.startswith(" ")
        assert not result.endswith(" ")
