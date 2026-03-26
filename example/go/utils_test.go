// Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
// SPDX-License-Identifier: MIT

package utils

import (
	"strings"
	"testing"
)

// TestCalculateAverage tests the CalculateAverage function with various inputs
func TestCalculateAverage(t *testing.T) {
	tests := []struct {
		name    string
		numbers []float64
		want    float64
		wantErr bool
	}{
		// Happy paths
		{
			name:    "single number",
			numbers: []float64{5},
			want:    5,
			wantErr: false,
		},
		{
			name:    "two numbers",
			numbers: []float64{2, 4},
			want:    3,
			wantErr: false,
		},
		{
			name:    "multiple numbers",
			numbers: []float64{1, 2, 3, 4, 5},
			want:    3,
			wantErr: false,
		},
		{
			name:    "negative numbers",
			numbers: []float64{-5, -3, -1},
			want:    -3,
			wantErr: false,
		},
		{
			name:    "mixed positive and negative",
			numbers: []float64{-10, 0, 10},
			want:    0,
			wantErr: false,
		},
		{
			name:    "decimal numbers",
			numbers: []float64{1.5, 2.5, 3.5},
			want:    2.5,
			wantErr: false,
		},
		{
			name:    "large numbers",
			numbers: []float64{1e10, 2e10, 3e10},
			want:    2e10,
			wantErr: false,
		},
		{
			name:    "very small numbers",
			numbers: []float64{1e-10, 2e-10, 3e-10},
			want:    2e-10,
			wantErr: false,
		},
		{
			name:    "zeros",
			numbers: []float64{0, 0, 0},
			want:    0,
			wantErr: false,
		},
		// Edge cases
		{
			name:    "empty slice error",
			numbers: []float64{},
			want:    0,
			wantErr: true,
		},
		{
			name:    "nil slice error",
			numbers: nil,
			want:    0,
			wantErr: true,
		},
		{
			name:    "single zero",
			numbers: []float64{0},
			want:    0,
			wantErr: false,
		},
		{
			name:    "many identical numbers",
			numbers: []float64{42, 42, 42, 42},
			want:    42,
			wantErr: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := CalculateAverage(tt.numbers)

			// Check error condition
			if (err != nil) != tt.wantErr {
				t.Errorf("CalculateAverage() error = %v, wantErr %v", err, tt.wantErr)
				return
			}

			// Check result value (with floating point tolerance)
			if got != tt.want {
				t.Errorf("CalculateAverage() = %v, want %v", got, tt.want)
			}
		})
	}
}

// TestCalculateAveragePrecision tests floating point precision
func TestCalculateAveragePrecision(t *testing.T) {
	// Test that division is accurate
	numbers := []float64{1, 2, 3}
	result, _ := CalculateAverage(numbers)
	expected := 2.0

	if result != expected {
		t.Errorf("CalculateAverage precision test: got %v, want %v", result, expected)
	}
}

// TestFizzBuzz tests the FizzBuzz function with various inputs
func TestFizzBuzz(t *testing.T) {
	tests := []struct {
		name     string
		input    int
		expected string
	}{
		// Happy paths - FizzBuzz numbers
		{
			name:     "15 is fizzbuzz",
			input:    15,
			expected: "fizzbuzz",
		},
		{
			name:     "30 is fizzbuzz",
			input:    30,
			expected: "fizzbuzz",
		},
		{
			name:     "45 is fizzbuzz",
			input:    45,
			expected: "fizzbuzz",
		},
		// Happy paths - Fizz numbers
		{
			name:     "3 is fizz",
			input:    3,
			expected: "fizz",
		},
		{
			name:     "6 is fizz",
			input:    6,
			expected: "fizz",
		},
		{
			name:     "9 is fizz",
			input:    9,
			expected: "fizz",
		},
		{
			name:     "12 is fizz",
			input:    12,
			expected: "fizz",
		},
		// Happy paths - Buzz numbers
		{
			name:     "5 is buzz",
			input:    5,
			expected: "buzz",
		},
		{
			name:     "10 is buzz",
			input:    10,
			expected: "buzz",
		},
		{
			name:     "20 is buzz",
			input:    20,
			expected: "buzz",
		},
		{
			name:     "25 is buzz",
			input:    25,
			expected: "buzz",
		},
		// Happy paths - Regular numbers
		{
			name:     "1 is one",
			input:    1,
			expected: "1",
		},
		{
			name:     "2 is two",
			input:    2,
			expected: "2",
		},
		{
			name:     "4 is four",
			input:    4,
			expected: "4",
		},
		{
			name:     "7 is seven",
			input:    7,
			expected: "7",
		},
		{
			name:     "8 is eight",
			input:    8,
			expected: "8",
		},
		{
			name:     "11 is eleven",
			input:    11,
			expected: "11",
		},
		// Edge cases - Boundary numbers
		{
			name:     "zero is zero",
			input:    0,
			expected: "fizzbuzz", // 0 % 15 == 0
		},
		{
			name:     "negative one",
			input:    -1,
			expected: "-1",
		},
		{
			name:     "negative fizz",
			input:    -3,
			expected: "fizz",
		},
		{
			name:     "negative buzz",
			input:    -5,
			expected: "buzz",
		},
		{
			name:     "negative fizzbuzz",
			input:    -15,
			expected: "fizzbuzz",
		},
		{
			name:     "large number",
			input:    1000000,
			expected: "buzz",
		},
		{
			name:     "large fizzbuzz",
			input:    999990,
			expected: "fizzbuzz",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := FizzBuzz(tt.input)
			if result != tt.expected {
				t.Errorf("FizzBuzz(%d) = %q, want %q", tt.input, result, tt.expected)
			}
		})
	}
}

// TestFizzBuzzPattern verifies the priority order (fizzbuzz > fizz > buzz > number)
func TestFizzBuzzPattern(t *testing.T) {
	// Verify that multiples of both 3 and 5 return "fizzbuzz", not "fizz" or "buzz"
	fizzbuzzNumbers := []int{15, 30, 45, 60, 75, 90, 105}
	for _, n := range fizzbuzzNumbers {
		result := FizzBuzz(n)
		if result != "fizzbuzz" {
			t.Errorf("FizzBuzz(%d) = %q, expected fizzbuzz (multiple of both 3 and 5)", n, result)
		}
	}

	// Verify that multiples of only 3 return "fizz"
	fizzNumbers := []int{3, 6, 9, 12, 18, 21, 24}
	for _, n := range fizzNumbers {
		result := FizzBuzz(n)
		if result != "fizz" {
			t.Errorf("FizzBuzz(%d) = %q, expected fizz (multiple of 3 only)", n, result)
		}
	}

	// Verify that multiples of only 5 return "buzz"
	buzzNumbers := []int{5, 10, 20, 25, 35, 40, 50}
	for _, n := range buzzNumbers {
		result := FizzBuzz(n)
		if result != "buzz" {
			t.Errorf("FizzBuzz(%d) = %q, expected buzz (multiple of 5 only)", n, result)
		}
	}
}

// TestReverseWords tests the ReverseWords function with various inputs
func TestReverseWords(t *testing.T) {
	tests := []struct {
		name     string
		input    string
		expected string
	}{
		// Happy paths
		{
			name:     "simple sentence",
			input:    "hello world",
			expected: "world hello",
		},
		{
			name:     "three words",
			input:    "the quick brown",
			expected: "brown quick the",
		},
		{
			name:     "four words",
			input:    "one two three four",
			expected: "four three two one",
		},
		// Edge cases - Single words
		{
			name:     "single word",
			input:    "hello",
			expected: "hello",
		},
		{
			name:     "empty string",
			input:    "",
			expected: "",
		},
		// Edge cases - Whitespace
		{
			name:     "leading whitespace",
			input:    "  hello world",
			expected: "world hello",
		},
		{
			name:     "trailing whitespace",
			input:    "hello world  ",
			expected: "world hello",
		},
		{
			name:     "multiple spaces between words",
			input:    "hello    world",
			expected: "world hello",
		},
		{
			name:     "tabs and spaces",
			input:    "hello\t\tworld",
			expected: "world hello",
		},
		{
			name:     "mixed whitespace",
			input:    "  hello  \t  world  ",
			expected: "world hello",
		},
		// Edge cases - Special cases
		{
			name:     "only spaces",
			input:    "   ",
			expected: "",
		},
		{
			name:     "only tabs",
			input:    "\t\t\t",
			expected: "",
		},
		{
			name:     "words with punctuation",
			input:    "hello, world!",
			expected: "world! hello,",
		},
		{
			name:     "words with numbers",
			input:    "abc 123 xyz",
			expected: "xyz 123 abc",
		},
		{
			name:     "words with special characters",
			input:    "test@123 sample#456 hello",
			expected: "hello sample#456 test@123",
		},
		// Happy paths - Longer sentences
		{
			name:     "longer sentence",
			input:    "The quick brown fox jumps over lazy dog",
			expected: "dog lazy over jumps fox brown quick The",
		},
		{
			name:     "sentence with repeated words",
			input:    "the the the",
			expected: "the the the",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := ReverseWords(tt.input)
			if result != tt.expected {
				t.Errorf("ReverseWords(%q) = %q, want %q", tt.input, result, tt.expected)
			}
		})
	}
}

// TestReverseWordsConsistency tests that reversing twice gives original
func TestReverseWordsConsistency(t *testing.T) {
	testCases := []string{
		"hello world",
		"one two three four five",
		"a",
		"test sentence with many words",
	}

	for _, sentence := range testCases {
		t.Run(sentence, func(t *testing.T) {
			reversed := ReverseWords(sentence)
			doubleReversed := ReverseWords(reversed)

			if sentence != doubleReversed {
				t.Errorf("ReverseWords is not consistent: original %q, double reversed %q", sentence, doubleReversed)
			}
		})
	}
}

// TestReverseWordsPreservesContent tests that content is preserved
func TestReverseWordsPreservesContent(t *testing.T) {
	input := "Hello World Test"
	result := ReverseWords(input)
	expected := "Test World Hello"

	if result != expected {
		t.Errorf("ReverseWords(%q) = %q, want %q", input, result, expected)
	}

	// Verify word count is preserved
	inputWords := len(strings.Fields(input))
	resultWords := len(strings.Fields(result))

	if inputWords != resultWords {
		t.Errorf("Word count changed: input %d, result %d", inputWords, resultWords)
	}
}
