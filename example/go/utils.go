// Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
// SPDX-License-Identifier: MIT

// Package utils provides simple utility functions for testing pipewright's
// test-gen workflow.
package utils

import (
	"errors"
	"fmt"
	"strings"
)

// CalculateAverage returns the arithmetic mean of a slice of float64 values.
// Returns an error if the slice is empty.
func CalculateAverage(numbers []float64) (float64, error) {
	if len(numbers) == 0 {
		return 0, errors.New("input must be a non-empty slice")
	}
	var total float64
	for _, n := range numbers {
		total += n
	}
	return total / float64(len(numbers)), nil
}

// FizzBuzz returns "fizz", "buzz", "fizzbuzz", or the number as a string.
func FizzBuzz(n int) string {
	switch {
	case n%15 == 0:
		return "fizzbuzz"
	case n%3 == 0:
		return "fizz"
	case n%5 == 0:
		return "buzz"
	default:
		return fmt.Sprintf("%d", n)
	}
}

// ReverseWords reverses the order of words in a sentence.
func ReverseWords(sentence string) string {
	words := strings.Fields(sentence)
	for i, j := 0, len(words)-1; i < j; i, j = i+1, j-1 {
		words[i], words[j] = words[j], words[i]
	}
	return strings.Join(words, " ")
}
