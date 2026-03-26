// Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
// SPDX-License-Identifier: MIT

/**
 * Comprehensive test suite for utils.js
 * Tests cover: happy paths, edge cases, and error handling
 */

const { calculateAverage, fizzBuzz, reverseWords } = require('./utils');

describe('calculateAverage', () => {
  // Happy paths
  describe('happy paths', () => {
    test('should calculate average of positive numbers', () => {
      expect(calculateAverage([1, 2, 3, 4, 5])).toBe(3);
    });

    test('should calculate average of a single number', () => {
      expect(calculateAverage([5])).toBe(5);
    });

    test('should calculate average of two numbers', () => {
      expect(calculateAverage([10, 20])).toBe(15);
    });

    test('should handle negative numbers', () => {
      expect(calculateAverage([-1, -2, -3])).toBe(-2);
    });

    test('should handle mixed positive and negative numbers', () => {
      expect(calculateAverage([-10, 0, 10])).toBe(0);
    });

    test('should handle decimal numbers', () => {
      expect(calculateAverage([1.5, 2.5, 3.5])).toBeCloseTo(2.5);
    });

    test('should handle very large numbers', () => {
      expect(calculateAverage([1000000, 2000000, 3000000])).toBe(2000000);
    });

    test('should handle very small decimal numbers', () => {
      expect(calculateAverage([0.001, 0.002, 0.003])).toBeCloseTo(0.002);
    });

    test('should handle zeros in array', () => {
      expect(calculateAverage([0, 0, 0, 1])).toBe(0.25);
    });
  });

  // Edge cases
  describe('edge cases', () => {
    test('should handle array with floating point precision', () => {
      const result = calculateAverage([0.1, 0.2, 0.3]);
      expect(result).toBeCloseTo(0.2);
    });

    test('should handle array with many elements', () => {
      const largeArray = Array(1000).fill(5);
      expect(calculateAverage(largeArray)).toBe(5);
    });

    test('should handle negative zero', () => {
      expect(calculateAverage([-0, 0, 0])).toBe(0);
    });
  });

  // Error handling
  describe('error handling', () => {
    test('should throw error for empty array', () => {
      expect(() => calculateAverage([])).toThrow('Input must be a non-empty array');
    });

    test('should throw error for null input', () => {
      expect(() => calculateAverage(null)).toThrow('Input must be a non-empty array');
    });

    test('should throw error for undefined input', () => {
      expect(() => calculateAverage(undefined)).toThrow('Input must be a non-empty array');
    });

    test('should throw error for non-array input (string)', () => {
      expect(() => calculateAverage('1,2,3')).toThrow('Input must be a non-empty array');
    });

    test('should throw error for non-array input (object)', () => {
      expect(() => calculateAverage({ numbers: [1, 2, 3] })).toThrow('Input must be a non-empty array');
    });

    test('should throw error for non-array input (number)', () => {
      expect(() => calculateAverage(42)).toThrow('Input must be a non-empty array');
    });
  });
});

describe('fizzBuzz', () => {
  // Happy paths
  describe('happy paths', () => {
    test('should return "fizz" for multiple of 3', () => {
      expect(fizzBuzz(3)).toBe('fizz');
      expect(fizzBuzz(6)).toBe('fizz');
      expect(fizzBuzz(9)).toBe('fizz');
      expect(fizzBuzz(12)).toBe('fizz');
    });

    test('should return "buzz" for multiple of 5', () => {
      expect(fizzBuzz(5)).toBe('buzz');
      expect(fizzBuzz(10)).toBe('buzz');
      expect(fizzBuzz(20)).toBe('buzz');
      expect(fizzBuzz(25)).toBe('buzz');
    });

    test('should return "fizzbuzz" for multiple of 15', () => {
      expect(fizzBuzz(15)).toBe('fizzbuzz');
      expect(fizzBuzz(30)).toBe('fizzbuzz');
      expect(fizzBuzz(45)).toBe('fizzbuzz');
      expect(fizzBuzz(60)).toBe('fizzbuzz');
    });

    test('should return number as string for non-multiples', () => {
      expect(fizzBuzz(1)).toBe('1');
      expect(fizzBuzz(2)).toBe('2');
      expect(fizzBuzz(4)).toBe('4');
      expect(fizzBuzz(7)).toBe('7');
      expect(fizzBuzz(8)).toBe('8');
      expect(fizzBuzz(11)).toBe('11');
      expect(fizzBuzz(13)).toBe('13');
      expect(fizzBuzz(14)).toBe('14');
      expect(fizzBuzz(16)).toBe('16');
    });

    test('should handle zero', () => {
      expect(fizzBuzz(0)).toBe('fizzbuzz');
    });

    test('should handle large multiples', () => {
      expect(fizzBuzz(300)).toBe('fizzbuzz');
      expect(fizzBuzz(333)).toBe('fizz');
      expect(fizzBuzz(500)).toBe('buzz');
    });
  });

  // Edge cases
  describe('edge cases', () => {
    test('should handle negative multiples of 3', () => {
      expect(fizzBuzz(-3)).toBe('fizz');
      expect(fizzBuzz(-6)).toBe('fizz');
    });

    test('should handle negative multiples of 5', () => {
      expect(fizzBuzz(-5)).toBe('buzz');
      expect(fizzBuzz(-10)).toBe('buzz');
    });

    test('should handle negative multiples of 15', () => {
      expect(fizzBuzz(-15)).toBe('fizzbuzz');
      expect(fizzBuzz(-30)).toBe('fizzbuzz');
    });

    test('should handle negative non-multiples', () => {
      expect(fizzBuzz(-1)).toBe('-1');
      expect(fizzBuzz(-7)).toBe('-7');
      expect(fizzBuzz(-14)).toBe('-14');
    });

    test('should return string representation of number', () => {
      const result = fizzBuzz(42);
      expect(typeof result).toBe('string');
      expect(result).toBe('fizz'); // 42 is divisible by 3
    });
  });

  // Error handling
  describe('error handling', () => {
    test('should handle floating point numbers', () => {
      // JavaScript floats are converted to string directly when not divisible by 3, 5, or 15
      expect(fizzBuzz(3.7)).toBe('3.7');
      expect(fizzBuzz(5.2)).toBe('5.2');
      expect(fizzBuzz(15.9)).toBe('15.9');
    });

    test('should handle NaN gracefully', () => {
      // NaN % any number returns NaN, which is not === to 0
      const result = fizzBuzz(NaN);
      expect(result).toBe('NaN');
    });

    test('should handle Infinity', () => {
      // Infinity % any number returns NaN
      const result = fizzBuzz(Infinity);
      expect(result).toBe('Infinity');
    });
  });
});

describe('reverseWords', () => {
  // Happy paths
  describe('happy paths', () => {
    test('should reverse order of words in a sentence', () => {
      expect(reverseWords('hello world')).toBe('world hello');
    });

    test('should reverse order of multiple words', () => {
      expect(reverseWords('one two three four')).toBe('four three two one');
    });

    test('should handle single word', () => {
      expect(reverseWords('hello')).toBe('hello');
    });

    test('should handle two words', () => {
      expect(reverseWords('foo bar')).toBe('bar foo');
    });

    test('should preserve word content', () => {
      expect(reverseWords('The Quick Brown Fox')).toBe('Fox Brown Quick The');
    });

    test('should handle punctuation attached to words', () => {
      expect(reverseWords('Hello, world!')).toBe('world! Hello,');
    });

    test('should handle mixed case', () => {
      expect(reverseWords('JavaScript is AWESOME')).toBe('AWESOME is JavaScript');
    });

    test('should handle special characters in words', () => {
      expect(reverseWords('hello-world foo_bar')).toBe('foo_bar hello-world');
    });
  });

  // Edge cases
  describe('edge cases', () => {
    test('should handle leading whitespace', () => {
      expect(reverseWords('  hello world')).toBe('world hello');
    });

    test('should handle trailing whitespace', () => {
      expect(reverseWords('hello world  ')).toBe('world hello');
    });

    test('should handle leading and trailing whitespace', () => {
      expect(reverseWords('  hello world  ')).toBe('world hello');
    });

    test('should handle multiple spaces between words', () => {
      expect(reverseWords('hello    world')).toBe('world hello');
    });

    test('should handle tabs and newlines as word separators', () => {
      expect(reverseWords('hello\tworld\nfoo')).toBe('foo world hello');
    });

    test('should handle mixed whitespace characters', () => {
      expect(reverseWords('one  \t  two   \n   three')).toBe('three two one');
    });

    test('should handle empty string', () => {
      expect(reverseWords('')).toBe('');
    });

    test('should handle string with only whitespace', () => {
      expect(reverseWords('   ')).toBe('');
    });

    test('should handle tabs', () => {
      expect(reverseWords('hello\tworld')).toBe('world hello');
    });

    test('should handle newlines', () => {
      expect(reverseWords('hello\nworld')).toBe('world hello');
    });

    test('should handle very long sentence', () => {
      const words = Array(100).fill('word');
      const sentence = words.join(' ');
      const result = reverseWords(sentence);
      const reversed = words.reverse().join(' ');
      expect(result).toBe(reversed);
    });

    test('should handle unicode characters', () => {
      expect(reverseWords('hello 世界')).toBe('世界 hello');
    });

    test('should handle emoji', () => {
      expect(reverseWords('hello 👋 world')).toBe('world 👋 hello');
    });
  });

  // Error handling
  describe('error handling', () => {
    test('should handle null by calling trim on it', () => {
      expect(() => reverseWords(null)).toThrow();
    });

    test('should handle undefined by calling trim on it', () => {
      expect(() => reverseWords(undefined)).toThrow();
    });

    test('should handle numeric input by calling trim on it', () => {
      expect(() => reverseWords(123)).toThrow();
    });
  });
});
