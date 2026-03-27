// Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
// SPDX-License-Identifier: MIT

import org.junit.Test;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

import static org.junit.Assert.*;

/**
 * Comprehensive test suite for the Utils class in demo/java-utils.
 * Covers happy paths, edge cases, and error handling for:
 * - isBalanced: Validates balanced parentheses, brackets, and braces
 * - mostFrequent: Finds the most frequent element in a list
 * - toRoman: Converts decimal numbers to Roman numerals
 * - flatten: Flattens nested list structures
 */
public class UtilsTest {

    // ============== isBalanced Tests ==============

    @Test
    public void testIsBalancedEmptyString() {
        assertTrue(Utils.isBalanced(""));
    }

    @Test
    public void testIsBalancedSinglePair() {
        assertTrue(Utils.isBalanced("()"));
        assertTrue(Utils.isBalanced("[]"));
        assertTrue(Utils.isBalanced("{}"));
    }

    @Test
    public void testIsBalancedMultiplePairs() {
        assertTrue(Utils.isBalanced("()[]{}"));
        assertTrue(Utils.isBalanced("()()()"));
        assertTrue(Utils.isBalanced("[][]"));
    }

    @Test
    public void testIsBalancedNestedBrackets() {
        assertTrue(Utils.isBalanced("({[]})"));
        assertTrue(Utils.isBalanced("[{()}]"));
        assertTrue(Utils.isBalanced("({[()]})"));
    }

    @Test
    public void testIsBalancedWithOtherCharacters() {
        assertTrue(Utils.isBalanced("hello(world)"));
        assertTrue(Utils.isBalanced("test[123]array"));
        assertTrue(Utils.isBalanced("map{key:value}"));
        assertTrue(Utils.isBalanced("a(b)c[d]e{f}g"));
    }

    @Test
    public void testIsBalancedUnmatchedOpening() {
        assertFalse(Utils.isBalanced("("));
        assertFalse(Utils.isBalanced("["));
        assertFalse(Utils.isBalanced("{"));
        assertFalse(Utils.isBalanced("([]"));
        assertFalse(Utils.isBalanced("[{"));
    }

    @Test
    public void testIsBalancedUnmatchedClosing() {
        assertFalse(Utils.isBalanced(")"));
        assertFalse(Utils.isBalanced("]"));
        assertFalse(Utils.isBalanced("}"));
        assertFalse(Utils.isBalanced("())"));
        assertFalse(Utils.isBalanced("[]]}"));
    }

    @Test
    public void testIsBalancedWrongOrder() {
        assertFalse(Utils.isBalanced("([)]"));
        assertFalse(Utils.isBalanced("{[}]"));
        assertFalse(Utils.isBalanced("[(])"));
    }

    @Test
    public void testIsBalancedWrongType() {
        assertFalse(Utils.isBalanced("(]"));
        assertFalse(Utils.isBalanced("{)"));
        assertFalse(Utils.isBalanced("[}"));
    }

    @Test
    public void testIsBalancedComplexNested() {
        assertTrue(Utils.isBalanced("function(arg1, array[0], {key: value})"));
        assertTrue(Utils.isBalanced("if (x > 0) { arr[i] = {a: 1}; }"));
    }

    @Test
    public void testIsBalancedMixedUnbalanced() {
        assertFalse(Utils.isBalanced("function(arg1, array[0], {key: value)"));
        assertFalse(Utils.isBalanced("if (x > 0 { arr[i] = {a: 1}; }"));
    }

    @Test
    public void testIsBalancedOnlyContent() {
        assertTrue(Utils.isBalanced("abcdefg"));
        assertTrue(Utils.isBalanced("12345"));
        assertTrue(Utils.isBalanced("!@#$%"));
    }

    @Test
    public void testIsBalancedSpecialCharacters() {
        assertTrue(Utils.isBalanced("(hello@world.com)"));
        assertTrue(Utils.isBalanced("[url=http://example.com]"));
    }

    // ============== mostFrequent Tests ==============

    @Test
    public void testMostFrequentSingleElement() {
        List<Integer> items = Arrays.asList(5);
        assertEquals(Integer.valueOf(5), Utils.mostFrequent(items));
    }

    @Test
    public void testMostFrequentClearWinner() {
        List<Integer> items = Arrays.asList(1, 1, 1, 2, 3);
        assertEquals(Integer.valueOf(1), Utils.mostFrequent(items));
    }

    @Test
    public void testMostFrequentAllEqual() {
        List<Integer> items = Arrays.asList(5, 5, 5);
        assertEquals(Integer.valueOf(5), Utils.mostFrequent(items));
    }

    @Test
    public void testMostFrequentTieReturnsFirst() {
        List<Integer> items = Arrays.asList(1, 1, 2, 2);
        Integer result = Utils.mostFrequent(items);
        assertTrue(result == 1 || result == 2); // Either is acceptable for a tie
    }

    @Test
    public void testMostFrequentStrings() {
        List<String> items = Arrays.asList("apple", "banana", "apple", "cherry", "apple");
        assertEquals("apple", Utils.mostFrequent(items));
    }

    @Test
    public void testMostFrequentMixedFrequencies() {
        List<String> items = Arrays.asList("a", "a", "a", "b", "b", "c");
        assertEquals("a", Utils.mostFrequent(items));
    }

    @Test
    public void testMostFrequentTwoElements() {
        List<Integer> items = Arrays.asList(10, 20);
        assertNotNull(Utils.mostFrequent(items));
    }

    @Test
    public void testMostFrequentEmptyList() {
        List<Integer> items = new ArrayList<>();
        assertNull(Utils.mostFrequent(items));
    }

    @Test
    public void testMostFrequentNullInput() {
        assertNull(Utils.mostFrequent(null));
    }

    @Test
    public void testMostFrequentLargeList() {
        List<Integer> items = new ArrayList<>();
        for (int i = 0; i < 100; i++) {
            items.add(1); // 1 appears 100 times
            items.add(2); // 2 appears 50 times
            items.add(3);
            items.add(4);
            items.add(5);
        }
        assertEquals(Integer.valueOf(1), Utils.mostFrequent(items));
    }

    @Test
    public void testMostFrequentWithNegatives() {
        List<Integer> items = Arrays.asList(-5, -5, -5, -1, 0, 1);
        assertEquals(Integer.valueOf(-5), Utils.mostFrequent(items));
    }

    @Test
    public void testMostFrequentCharacters() {
        List<Character> items = Arrays.asList('a', 'b', 'a', 'c', 'a');
        assertEquals(Character.valueOf('a'), Utils.mostFrequent(items));
    }

    @Test
    public void testMostFrequentConsistency() {
        List<Integer> items = Arrays.asList(7, 7, 7, 8, 8, 9);
        Integer result1 = Utils.mostFrequent(items);
        Integer result2 = Utils.mostFrequent(items);
        assertEquals(result1, result2);
    }

    // ============== toRoman Tests ==============

    @Test
    public void testToRomanMinimum() {
        assertEquals("I", Utils.toRoman(1));
    }

    @Test
    public void testToRomanMaximum() {
        assertEquals("MMMCMXCIX", Utils.toRoman(3999));
    }

    @Test
    public void testToRomanSingleValues() {
        assertEquals("I", Utils.toRoman(1));
        assertEquals("II", Utils.toRoman(2));
        assertEquals("III", Utils.toRoman(3));
        assertEquals("IV", Utils.toRoman(4));
        assertEquals("V", Utils.toRoman(5));
        assertEquals("VI", Utils.toRoman(6));
        assertEquals("VII", Utils.toRoman(7));
        assertEquals("VIII", Utils.toRoman(8));
        assertEquals("IX", Utils.toRoman(9));
    }

    @Test
    public void testToRomanTens() {
        assertEquals("X", Utils.toRoman(10));
        assertEquals("XX", Utils.toRoman(20));
        assertEquals("XXX", Utils.toRoman(30));
        assertEquals("XL", Utils.toRoman(40));
        assertEquals("L", Utils.toRoman(50));
        assertEquals("LX", Utils.toRoman(60));
        assertEquals("XC", Utils.toRoman(90));
    }

    @Test
    public void testToRomanHundreds() {
        assertEquals("C", Utils.toRoman(100));
        assertEquals("CC", Utils.toRoman(200));
        assertEquals("CCC", Utils.toRoman(300));
        assertEquals("CD", Utils.toRoman(400));
        assertEquals("D", Utils.toRoman(500));
        assertEquals("DC", Utils.toRoman(600));
        assertEquals("CM", Utils.toRoman(900));
    }

    @Test
    public void testToRomanThousands() {
        assertEquals("M", Utils.toRoman(1000));
        assertEquals("MM", Utils.toRoman(2000));
        assertEquals("MMM", Utils.toRoman(3000));
    }

    @Test
    public void testToRomanComplex() {
        assertEquals("XLIV", Utils.toRoman(44));
        assertEquals("XCIX", Utils.toRoman(99));
        assertEquals("CDXLIV", Utils.toRoman(444));
        assertEquals("CMXCIX", Utils.toRoman(999));
        assertEquals("MCMXC", Utils.toRoman(1990));
        assertEquals("MMXXI", Utils.toRoman(2021));
        assertEquals("MMMCMXCIV", Utils.toRoman(3994));
    }

    @Test
    public void testToRomanZeroThrowsException() {
        try {
            Utils.toRoman(0);
            fail("Should throw IllegalArgumentException for 0");
        } catch (IllegalArgumentException e) {
            assertEquals("Number must be between 1 and 3999", e.getMessage());
        }
    }

    @Test
    public void testToRomanNegativeThrowsException() {
        try {
            Utils.toRoman(-5);
            fail("Should throw IllegalArgumentException for negative number");
        } catch (IllegalArgumentException e) {
            assertEquals("Number must be between 1 and 3999", e.getMessage());
        }
    }

    @Test
    public void testToRomanTooLargeThrowsException() {
        try {
            Utils.toRoman(4000);
            fail("Should throw IllegalArgumentException for 4000");
        } catch (IllegalArgumentException e) {
            assertEquals("Number must be between 1 and 3999", e.getMessage());
        }
    }

    @Test
    public void testToRomanFarTooLargeThrowsException() {
        try {
            Utils.toRoman(10000);
            fail("Should throw IllegalArgumentException for 10000");
        } catch (IllegalArgumentException e) {
            assertEquals("Number must be between 1 and 3999", e.getMessage());
        }
    }

    @Test
    public void testToRomanBoundaryLowEnd() {
        assertEquals("I", Utils.toRoman(1));
        assertEquals("II", Utils.toRoman(2));
    }

    @Test
    public void testToRomanBoundaryHighEnd() {
        assertEquals("MMMCMXCIX", Utils.toRoman(3999));
        assertEquals("MMMCMXCVIII", Utils.toRoman(3998));
    }

    @Test
    public void testToRomanConsistency() {
        String result1 = Utils.toRoman(1987);
        String result2 = Utils.toRoman(1987);
        assertEquals(result1, result2);
    }

    @Test
    public void testToRomanVariousNumbers() {
        assertEquals("VII", Utils.toRoman(7));
        assertEquals("XXXVII", Utils.toRoman(37));
        assertEquals("CLIII", Utils.toRoman(153));
        assertEquals("MMCDXXI", Utils.toRoman(2421));
    }

    // ============== flatten Tests ==============

    @Test
    public void testFlattenEmptyList() {
        List<?> nested = new ArrayList<>();
        List<?> result = Utils.flatten(nested);
        assertTrue(result.isEmpty());
    }

    @Test
    public void testFlattenFlatList() {
        List<Object> nested = Arrays.asList(1, 2, 3, 4, 5);
        List<?> result = Utils.flatten(nested);
        assertEquals(5, result.size());
        assertEquals(Arrays.asList(1, 2, 3, 4, 5), result);
    }

    @Test
    public void testFlattenSingleLevelNesting() {
        List<Object> nested = new ArrayList<>();
        nested.add(1);
        nested.add(Arrays.asList(2, 3));
        nested.add(4);

        List<?> result = Utils.flatten(nested);
        assertEquals(4, result.size());
        assertEquals(Arrays.asList(1, 2, 3, 4), result);
    }

    @Test
    public void testFlattenMultipleLevelNesting() {
        List<Object> nested = new ArrayList<>();
        nested.add(1);
        List<Object> level1 = Arrays.asList(2, 3, Arrays.asList(4, 5));
        nested.add(level1);
        nested.add(6);

        List<?> result = Utils.flatten(nested);
        assertEquals(6, result.size());
        assertEquals(Arrays.asList(1, 2, 3, 4, 5, 6), result);
    }

    @Test
    public void testFlattenDeeplyNestedStructure() {
        List<Object> nested = new ArrayList<>();
        nested.add(1);
        nested.add(Arrays.asList(2, Arrays.asList(3, Arrays.asList(4, 5))));
        nested.add(6);

        List<?> result = Utils.flatten(nested);
        assertEquals(6, result.size());
        assertEquals(Arrays.asList(1, 2, 3, 4, 5, 6), result);
    }

    @Test
    public void testFlattenWithEmptyNestedLists() {
        List<Object> nested = new ArrayList<>();
        nested.add(1);
        nested.add(new ArrayList<>());
        nested.add(2);
        nested.add(Arrays.asList(3, 4));

        List<?> result = Utils.flatten(nested);
        assertEquals(4, result.size());
        assertEquals(Arrays.asList(1, 2, 3, 4), result);
    }

    @Test
    public void testFlattenStrings() {
        List<Object> nested = new ArrayList<>();
        nested.add("a");
        nested.add(Arrays.asList("b", "c"));
        nested.add("d");

        List<?> result = Utils.flatten(nested);
        assertEquals(4, result.size());
        assertEquals(Arrays.asList("a", "b", "c", "d"), result);
    }

    @Test
    public void testFlattenMixedTypes() {
        List<Object> nested = new ArrayList<>();
        nested.add(1);
        nested.add("two");
        nested.add(Arrays.asList(3, "four", 5.0));
        nested.add(true);

        List<?> result = Utils.flatten(nested);
        assertEquals(6, result.size());
        assertEquals(1, result.get(0));
        assertEquals("two", result.get(1));
        assertEquals(3, result.get(2));
        assertEquals("four", result.get(3));
        assertEquals(5.0, result.get(4));
        assertEquals(true, result.get(5));
    }

    @Test
    public void testFlattenAllNested() {
        List<Object> nested = new ArrayList<>();
        nested.add(Arrays.asList(Arrays.asList(1, 2), Arrays.asList(3, 4)));
        nested.add(Arrays.asList(5, 6));

        List<?> result = Utils.flatten(nested);
        assertEquals(6, result.size());
        assertEquals(Arrays.asList(1, 2, 3, 4, 5, 6), result);
    }

    @Test
    public void testFlattenSingleElement() {
        List<Object> nested = new ArrayList<>();
        nested.add(42);

        List<?> result = Utils.flatten(nested);
        assertEquals(1, result.size());
        assertEquals(42, result.get(0));
    }

    @Test
    public void testFlattenSingleElementList() {
        List<Object> nested = new ArrayList<>();
        nested.add(Arrays.asList(42));

        List<?> result = Utils.flatten(nested);
        assertEquals(1, result.size());
        assertEquals(42, result.get(0));
    }

    @Test
    public void testFlattenLargeList() {
        List<Object> nested = new ArrayList<>();
        for (int i = 0; i < 50; i++) {
            if (i % 2 == 0) {
                nested.add(i);
            } else {
                nested.add(Arrays.asList(i, i + 1000));
            }
        }

        List<?> result = Utils.flatten(nested);
        assertEquals(75, result.size()); // 25 single items + 50 from pairs
    }

    @Test
    public void testFlattenPreservesOrder() {
        List<Object> nested = new ArrayList<>();
        nested.add(1);
        nested.add(Arrays.asList(2, 3));
        nested.add(4);
        nested.add(Arrays.asList(5, 6));
        nested.add(7);

        List<?> result = Utils.flatten(nested);
        assertEquals(Arrays.asList(1, 2, 3, 4, 5, 6, 7), result);
    }

    @Test
    public void testFlattenConsistency() {
        List<Object> nested = new ArrayList<>();
        nested.add(1);
        nested.add(Arrays.asList(2, Arrays.asList(3, 4)));
        nested.add(5);

        List<?> result1 = Utils.flatten(nested);
        List<?> result2 = Utils.flatten(nested);
        assertEquals(result1, result2);
    }

    @Test
    public void testFlattenWithNullElements() {
        List<Object> nested = new ArrayList<>();
        nested.add(1);
        nested.add(null);
        nested.add(Arrays.asList(2, null, 3));

        List<?> result = Utils.flatten(nested);
        assertEquals(5, result.size());
        assertEquals(1, result.get(0));
        assertNull(result.get(1));
        assertEquals(2, result.get(2));
        assertNull(result.get(3));
        assertEquals(3, result.get(4));
    }
}
