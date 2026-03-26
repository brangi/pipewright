// Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
// SPDX-License-Identifier: MIT

import { describe, it, expect } from "vitest";
import { calculateAverage, fizzBuzz, reverseWords } from "./utils";

describe("calculateAverage", () => {
  // Happy paths
  it("should calculate the average of positive numbers", () => {
    expect(calculateAverage([1, 2, 3])).toBe(2);
  });

  it("should calculate the average of a single number", () => {
    expect(calculateAverage([42])).toBe(42);
  });

  it("should calculate the average with decimal results", () => {
    expect(calculateAverage([1, 2, 3, 4, 5])).toBe(3);
  });

  it("should handle large numbers", () => {
    expect(calculateAverage([1000000, 2000000, 3000000])).toBe(2000000);
  });

  it("should handle negative numbers", () => {
    expect(calculateAverage([-5, -3, -1])).toBe(-3);
  });

  it("should handle mixed positive and negative numbers", () => {
    expect(calculateAverage([-2, 0, 2])).toBe(0);
  });

  it("should handle fractional numbers", () => {
    expect(calculateAverage([0.5, 1.5, 2.5])).toBe(1.5);
  });

  // Edge cases
  it("should handle zero values", () => {
    expect(calculateAverage([0, 0, 0])).toBe(0);
  });

  it("should calculate average with two numbers", () => {
    expect(calculateAverage([10, 20])).toBe(15);
  });

  it("should handle very small decimal numbers", () => {
    expect(calculateAverage([0.1, 0.2, 0.3])).toBeCloseTo(0.2, 5);
  });

  // Error handling
  it("should throw an error for empty array", () => {
    expect(() => calculateAverage([])).toThrow(
      "Input must be a non-empty array"
    );
  });

  it("should throw an Error instance", () => {
    expect(() => calculateAverage([])).toThrow(Error);
  });
});

describe("fizzBuzz", () => {
  // Happy paths - fizzbuzz
  it("should return 'fizzbuzz' for multiples of 15", () => {
    expect(fizzBuzz(15)).toBe("fizzbuzz");
    expect(fizzBuzz(30)).toBe("fizzbuzz");
    expect(fizzBuzz(45)).toBe("fizzbuzz");
  });

  // Happy paths - fizz
  it("should return 'fizz' for multiples of 3 only", () => {
    expect(fizzBuzz(3)).toBe("fizz");
    expect(fizzBuzz(6)).toBe("fizz");
    expect(fizzBuzz(9)).toBe("fizz");
  });

  it("should return 'fizz' for 3", () => {
    expect(fizzBuzz(3)).toBe("fizz");
  });

  // Happy paths - buzz
  it("should return 'buzz' for multiples of 5 only", () => {
    expect(fizzBuzz(5)).toBe("buzz");
    expect(fizzBuzz(10)).toBe("buzz");
    expect(fizzBuzz(20)).toBe("buzz");
  });

  it("should return 'buzz' for 5", () => {
    expect(fizzBuzz(5)).toBe("buzz");
  });

  // Happy paths - number as string
  it("should return the number as a string for other numbers", () => {
    expect(fizzBuzz(1)).toBe("1");
    expect(fizzBuzz(2)).toBe("2");
    expect(fizzBuzz(4)).toBe("4");
    expect(fizzBuzz(7)).toBe("7");
  });

  // Edge cases
  it("should handle zero", () => {
    expect(fizzBuzz(0)).toBe("fizzbuzz");
  });

  it("should handle negative multiples of 15", () => {
    expect(fizzBuzz(-15)).toBe("fizzbuzz");
    expect(fizzBuzz(-30)).toBe("fizzbuzz");
  });

  it("should handle negative multiples of 3", () => {
    expect(fizzBuzz(-3)).toBe("fizz");
    expect(fizzBuzz(-9)).toBe("fizz");
  });

  it("should handle negative multiples of 5", () => {
    expect(fizzBuzz(-5)).toBe("buzz");
    expect(fizzBuzz(-10)).toBe("buzz");
  });

  it("should handle negative non-multiples", () => {
    expect(fizzBuzz(-1)).toBe("-1");
    expect(fizzBuzz(-7)).toBe("-7");
  });

  it("should handle large numbers", () => {
    expect(fizzBuzz(1000001)).toBe("1000001");
    expect(fizzBuzz(9999999)).toBe("fizz");
  });

  // Boundary cases
  it("should correctly handle 12 (multiple of 3 but not 5)", () => {
    expect(fizzBuzz(12)).toBe("fizz");
  });

  it("should correctly handle 25 (multiple of 5 but not 3)", () => {
    expect(fizzBuzz(25)).toBe("buzz");
  });
});

describe("reverseWords", () => {
  // Happy paths
  it("should reverse the order of words in a simple sentence", () => {
    expect(reverseWords("hello world")).toBe("world hello");
  });

  it("should reverse three words", () => {
    expect(reverseWords("one two three")).toBe("three two one");
  });

  it("should reverse four words", () => {
    expect(reverseWords("the quick brown fox")).toBe("fox brown quick the");
  });

  it("should handle single word", () => {
    expect(reverseWords("hello")).toBe("hello");
  });

  // Edge cases - whitespace
  it("should handle leading whitespace", () => {
    expect(reverseWords("  hello world")).toBe("world hello");
  });

  it("should handle trailing whitespace", () => {
    expect(reverseWords("hello world  ")).toBe("world hello");
  });

  it("should handle multiple spaces between words", () => {
    expect(reverseWords("hello   world")).toBe("world hello");
  });

  it("should handle tabs and mixed whitespace", () => {
    expect(reverseWords("hello\t\nworld")).toBe("world hello");
  });

  it("should handle only whitespace in string", () => {
    expect(reverseWords("   ")).toBe("");
  });

  // Edge cases - empty and special characters
  it("should handle empty string", () => {
    expect(reverseWords("")).toBe("");
  });

  it("should preserve word content with punctuation", () => {
    expect(reverseWords("hello, world!")).toBe("world! hello,");
  });

  it("should handle words with numbers", () => {
    expect(reverseWords("test123 example456")).toBe("example456 test123");
  });

  it("should handle hyphenated words", () => {
    expect(reverseWords("hello-world test")).toBe("test hello-world");
  });

  it("should handle camelCase words", () => {
    expect(reverseWords("camelCase anotherWord")).toBe("anotherWord camelCase");
  });

  // Complex cases
  it("should handle sentence with special characters", () => {
    expect(reverseWords("Hello, World!")).toBe("World! Hello,");
  });

  it("should handle unicode characters", () => {
    expect(reverseWords("café restaurant")).toBe("restaurant café");
  });

  it("should handle many words", () => {
    expect(reverseWords("one two three four five")).toBe(
      "five four three two one"
    );
  });

  it("should maintain word integrity", () => {
    const result = reverseWords("alpha beta gamma");
    const words = result.split(" ");
    expect(words).toEqual(["gamma", "beta", "alpha"]);
  });
});
