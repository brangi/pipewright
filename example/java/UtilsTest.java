// Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
// SPDX-License-Identifier: MIT

import org.junit.Test;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

import static org.junit.Assert.*;

/**
 * Comprehensive test suite for the Utils class.
 * Covers happy paths, edge cases, and error handling.
 */
public class UtilsTest {

    // ============== calculateAverage Tests ==============

    @Test
    public void testCalculateAveragePositiveNumbers() {
        List<Double> numbers = Arrays.asList(1.0, 2.0, 3.0, 4.0, 5.0);
        double result = Utils.calculateAverage(numbers);
        assertEquals(3.0, result, 0.0001);
    }

    @Test
    public void testCalculateAverageMixedNumbers() {
        List<Double> numbers = Arrays.asList(-5.0, -2.5, 0.0, 2.5, 5.0);
        double result = Utils.calculateAverage(numbers);
        assertEquals(0.0, result, 0.0001);
    }

    @Test
    public void testCalculateAverageSingleElement() {
        List<Double> numbers = Arrays.asList(42.5);
        double result = Utils.calculateAverage(numbers);
        assertEquals(42.5, result, 0.0001);
    }

    @Test
    public void testCalculateAverageTwoElements() {
        List<Double> numbers = Arrays.asList(10.0, 20.0);
        double result = Utils.calculateAverage(numbers);
        assertEquals(15.0, result, 0.0001);
    }

    @Test
    public void testCalculateAverageLargeList() {
        List<Double> numbers = new ArrayList<>();
        for (int i = 1; i <= 100; i++) {
            numbers.add((double) i);
        }
        double result = Utils.calculateAverage(numbers);
        assertEquals(50.5, result, 0.0001);
    }

    @Test
    public void testCalculateAverageSmallDecimals() {
        List<Double> numbers = Arrays.asList(0.001, 0.002, 0.003);
        double result = Utils.calculateAverage(numbers);
        assertEquals(0.002, result, 0.0000001);
    }

    @Test
    public void testCalculateAverageNullInput() {
        try {
            Utils.calculateAverage(null);
            fail("Should throw IllegalArgumentException for null input");
        } catch (IllegalArgumentException e) {
            assertTrue(true); // Exception was thrown as expected
        }
    }

    @Test
    public void testCalculateAverageEmptyList() {
        List<Double> numbers = new ArrayList<>();
        try {
            Utils.calculateAverage(numbers);
            fail("Should throw IllegalArgumentException for empty list");
        } catch (IllegalArgumentException e) {
            assertTrue(true); // Exception was thrown as expected
        }
    }

    @Test
    public void testCalculateAverageEmptyListMessage() {
        List<Double> numbers = Collections.emptyList();
        try {
            Utils.calculateAverage(numbers);
            fail("Should throw IllegalArgumentException");
        } catch (IllegalArgumentException e) {
            assertEquals("Input must be a non-empty list", e.getMessage());
        }
    }

    @Test
    public void testCalculateAverageNegativeNumbers() {
        List<Double> numbers = Arrays.asList(-10.0, -20.0, -30.0);
        double result = Utils.calculateAverage(numbers);
        assertEquals(-20.0, result, 0.0001);
    }

    @Test
    public void testCalculateAverageWithZeros() {
        List<Double> numbers = Arrays.asList(0.0, 0.0, 0.0);
        double result = Utils.calculateAverage(numbers);
        assertEquals(0.0, result, 0.0001);
    }

    // ============== fizzBuzz Tests ==============

    @Test
    public void testFizzBuzzMultipleOfFifteen() {
        assertEquals("fizzbuzz", Utils.fizzBuzz(15));
        assertEquals("fizzbuzz", Utils.fizzBuzz(30));
        assertEquals("fizzbuzz", Utils.fizzBuzz(45));
    }

    @Test
    public void testFizzBuzzMultipleOfThree() {
        assertEquals("fizz", Utils.fizzBuzz(3));
        assertEquals("fizz", Utils.fizzBuzz(6));
        assertEquals("fizz", Utils.fizzBuzz(9));
        assertEquals("fizz", Utils.fizzBuzz(12));
        assertEquals("fizz", Utils.fizzBuzz(18));
    }

    @Test
    public void testFizzBuzzMultipleOfFive() {
        assertEquals("buzz", Utils.fizzBuzz(5));
        assertEquals("buzz", Utils.fizzBuzz(10));
        assertEquals("buzz", Utils.fizzBuzz(20));
        assertEquals("buzz", Utils.fizzBuzz(25));
    }

    @Test
    public void testFizzBuzzNonMultiple() {
        assertEquals("1", Utils.fizzBuzz(1));
        assertEquals("2", Utils.fizzBuzz(2));
        assertEquals("4", Utils.fizzBuzz(4));
        assertEquals("7", Utils.fizzBuzz(7));
        assertEquals("11", Utils.fizzBuzz(11));
    }

    @Test
    public void testFizzBuzzZero() {
        assertEquals("fizzbuzz", Utils.fizzBuzz(0));
    }

    @Test
    public void testFizzBuzzNegativeThree() {
        assertEquals("fizz", Utils.fizzBuzz(-3));
        assertEquals("fizz", Utils.fizzBuzz(-6));
        assertEquals("fizz", Utils.fizzBuzz(-12));
    }

    @Test
    public void testFizzBuzzNegativeFive() {
        assertEquals("buzz", Utils.fizzBuzz(-5));
        assertEquals("buzz", Utils.fizzBuzz(-10));
        assertEquals("buzz", Utils.fizzBuzz(-20));
    }

    @Test
    public void testFizzBuzzNegativeFifteen() {
        assertEquals("fizzbuzz", Utils.fizzBuzz(-15));
        assertEquals("fizzbuzz", Utils.fizzBuzz(-30));
    }

    @Test
    public void testFizzBuzzNegativeNonMultiple() {
        assertEquals("-1", Utils.fizzBuzz(-1));
        assertEquals("-2", Utils.fizzBuzz(-2));
        assertEquals("-7", Utils.fizzBuzz(-7));
    }

    @Test
    public void testFizzBuzzLargeMultiples() {
        assertEquals("fizz", Utils.fizzBuzz(999));
        assertEquals("buzz", Utils.fizzBuzz(1000));
        assertEquals("fizzbuzz", Utils.fizzBuzz(9999));
    }

    // ============== reverseWords Tests ==============

    @Test
    public void testReverseWordsSimpleSentence() {
        String result = Utils.reverseWords("hello world");
        assertEquals("world hello", result);
    }

    @Test
    public void testReverseWordsMultipleWords() {
        String result = Utils.reverseWords("the quick brown fox");
        assertEquals("fox brown quick the", result);
    }

    @Test
    public void testReverseWordsSingleWord() {
        String result = Utils.reverseWords("hello");
        assertEquals("hello", result);
    }

    @Test
    public void testReverseWordsExtraSpaces() {
        String result = Utils.reverseWords("hello    world    test");
        assertEquals("test world hello", result);
    }

    @Test
    public void testReverseWordsLeadingTrailingSpaces() {
        String result = Utils.reverseWords("  hello world  ");
        assertEquals("world hello", result);
    }

    @Test
    public void testReverseWordsMixedWhitespace() {
        String result = Utils.reverseWords("hello\t\tworld  \ntest");
        assertEquals("test world hello", result);
    }

    @Test
    public void testReverseWordsWithPunctuation() {
        String result = Utils.reverseWords("Hello, world!");
        assertEquals("world! Hello,", result);
    }

    @Test
    public void testReverseWordsEmptyString() {
        String result = Utils.reverseWords("");
        assertEquals("", result);
    }

    @Test
    public void testReverseWordsOnlySpaces() {
        String result = Utils.reverseWords("     ");
        assertEquals("", result);
    }

    @Test
    public void testReverseWordsLongSentence() {
        String input = "one two three four five six seven eight nine ten";
        String expected = "ten nine eight seven six five four three two one";
        String result = Utils.reverseWords(input);
        assertEquals(expected, result);
    }

    @Test
    public void testReverseWordsPreservesContent() {
        String result = Utils.reverseWords("abc123 def456 ghi789");
        assertEquals("ghi789 def456 abc123", result);
    }

    @Test
    public void testReverseWordsUnicode() {
        String result = Utils.reverseWords("こんにちは 世界");
        assertEquals("世界 こんにちは", result);
    }

    @Test
    public void testReverseWordsConsistency() {
        String input = "java test suite";
        String result1 = Utils.reverseWords(input);
        String result2 = Utils.reverseWords(input);
        assertEquals(result1, result2);
    }

    @Test
    public void testReverseWordsReversibility() {
        String original = "first second third";
        String reversed = Utils.reverseWords(original);
        String doubleReversed = Utils.reverseWords(reversed);
        assertEquals(original, doubleReversed);
    }

    @Test
    public void testReverseWordsBasic1() {
        assertEquals("world hello", Utils.reverseWords("hello world"));
    }

    @Test
    public void testReverseWordsBasic2() {
        assertEquals("three two one", Utils.reverseWords("one two three"));
    }

    @Test
    public void testReverseWordsBasic3() {
        assertEquals("single", Utils.reverseWords("single"));
    }

    @Test
    public void testReverseWordsBasic4() {
        assertEquals("words spaced", Utils.reverseWords("  spaced  words  "));
    }
}
