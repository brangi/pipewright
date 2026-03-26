// Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
// SPDX-License-Identifier: MIT

/**
 * Simple utility functions for testing pipewright's test-gen workflow.
 */

/**
 * Calculate the average of an array of numbers.
 * @param {number[]} numbers
 * @returns {number}
 */
function calculateAverage(numbers) {
  if (!Array.isArray(numbers) || numbers.length === 0) {
    throw new Error("Input must be a non-empty array");
  }
  const total = numbers.reduce((sum, n) => sum + n, 0);
  return total / numbers.length;
}

/**
 * Return "fizz", "buzz", "fizzbuzz", or the number as a string.
 * @param {number} n
 * @returns {string}
 */
function fizzBuzz(n) {
  if (n % 15 === 0) return "fizzbuzz";
  if (n % 3 === 0) return "fizz";
  if (n % 5 === 0) return "buzz";
  return String(n);
}

/**
 * Reverse the order of words in a sentence.
 * @param {string} sentence
 * @returns {string}
 */
function reverseWords(sentence) {
  return sentence.trim().split(/\s+/).reverse().join(" ");
}

module.exports = { calculateAverage, fizzBuzz, reverseWords };
