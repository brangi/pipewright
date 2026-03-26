// Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
// SPDX-License-Identifier: MIT

import java.util.List;

/**
 * Simple utility class for testing pipewright's test-gen workflow.
 */
public class Utils {

    /**
     * Calculate the average of a list of numbers.
     *
     * @param numbers list of doubles
     * @return the arithmetic mean
     * @throws IllegalArgumentException if the list is empty
     */
    public static double calculateAverage(List<Double> numbers) {
        if (numbers == null || numbers.isEmpty()) {
            throw new IllegalArgumentException("Input must be a non-empty list");
        }
        double total = 0;
        for (double n : numbers) {
            total += n;
        }
        return total / numbers.size();
    }

    /**
     * Return "fizz", "buzz", "fizzbuzz", or the number as a string.
     *
     * @param n the input number
     * @return the fizzbuzz result
     */
    public static String fizzBuzz(int n) {
        if (n % 15 == 0) return "fizzbuzz";
        if (n % 3 == 0) return "fizz";
        if (n % 5 == 0) return "buzz";
        return String.valueOf(n);
    }

    /**
     * Reverse the order of words in a sentence.
     *
     * @param sentence the input string
     * @return the sentence with reversed word order
     */
    public static String reverseWords(String sentence) {
        String[] words = sentence.trim().split("\\s+");
        StringBuilder result = new StringBuilder();
        for (int i = words.length - 1; i >= 0; i--) {
            result.append(words[i]);
            if (i > 0) result.append(" ");
        }
        return result.toString();
    }
}
