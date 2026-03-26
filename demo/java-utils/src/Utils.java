// Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
// SPDX-License-Identifier: MIT

import java.util.*;
import java.util.stream.Collectors;

/**
 * Utility class for the pipewright Java demo.
 */
public class Utils {

    /**
     * Check if a string contains only balanced parentheses, brackets, and braces.
     *
     * @param input the string to check
     * @return true if balanced, false otherwise
     */
    public static boolean isBalanced(String input) {
        Deque<Character> stack = new ArrayDeque<>();
        Map<Character, Character> pairs = Map.of(')', '(', ']', '[', '}', '{');

        for (char c : input.toCharArray()) {
            if (pairs.containsValue(c)) {
                stack.push(c);
            } else if (pairs.containsKey(c)) {
                if (stack.isEmpty() || !stack.pop().equals(pairs.get(c))) {
                    return false;
                }
            }
        }
        return stack.isEmpty();
    }

    /**
     * Find the most frequent element in a list.
     * Returns null if the list is empty.
     *
     * @param items the list of items
     * @param <T> the element type
     * @return the most frequent element, or null
     */
    public static <T> T mostFrequent(List<T> items) {
        if (items == null || items.isEmpty()) return null;

        Map<T, Long> freq = items.stream()
                .collect(Collectors.groupingBy(i -> i, Collectors.counting()));

        return freq.entrySet().stream()
                .max(Map.Entry.comparingByValue())
                .map(Map.Entry::getKey)
                .orElse(null);
    }

    /**
     * Convert a decimal number to a Roman numeral string.
     * Supports values from 1 to 3999.
     *
     * @param num the number to convert
     * @return the Roman numeral string
     * @throws IllegalArgumentException if num is out of range
     */
    public static String toRoman(int num) {
        if (num < 1 || num > 3999) {
            throw new IllegalArgumentException("Number must be between 1 and 3999");
        }

        int[] values = {1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1};
        String[] symbols = {"M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"};

        StringBuilder result = new StringBuilder();
        for (int i = 0; i < values.length; i++) {
            while (num >= values[i]) {
                result.append(symbols[i]);
                num -= values[i];
            }
        }
        return result.toString();
    }

    /**
     * Flatten a nested list structure into a single list.
     *
     * @param nested the nested list (elements can be items or lists)
     * @param <T> the element type
     * @return a flat list of all elements
     */
    @SuppressWarnings("unchecked")
    public static <T> List<T> flatten(List<?> nested) {
        List<T> result = new ArrayList<>();
        for (Object item : nested) {
            if (item instanceof List) {
                result.addAll(flatten((List<?>) item));
            } else {
                result.add((T) item);
            }
        }
        return result;
    }
}
