// Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
// SPDX-License-Identifier: MIT

//! Comprehensive tests for pipewright-rust-example library functions.

use pipewright_rust_example::{calculate_average, fizzbuzz, reverse_words};

// ============================================================================
// Tests for calculate_average
// ============================================================================

#[test]
fn test_calculate_average_simple() {
    let numbers = vec![1.0, 2.0, 3.0];
    let result = calculate_average(&numbers);
    assert_eq!(result, Ok(2.0));
}

#[test]
fn test_calculate_average_single_element() {
    let numbers = vec![5.0];
    let result = calculate_average(&numbers);
    assert_eq!(result, Ok(5.0));
}

#[test]
fn test_calculate_average_two_elements() {
    let numbers = vec![10.0, 20.0];
    let result = calculate_average(&numbers);
    assert_eq!(result, Ok(15.0));
}

#[test]
fn test_calculate_average_large_numbers() {
    let numbers = vec![1_000_000.0, 2_000_000.0, 3_000_000.0];
    let result = calculate_average(&numbers);
    assert_eq!(result, Ok(2_000_000.0));
}

#[test]
fn test_calculate_average_negative_numbers() {
    let numbers = vec![-1.0, -2.0, -3.0];
    let result = calculate_average(&numbers);
    assert_eq!(result, Ok(-2.0));
}

#[test]
fn test_calculate_average_mixed_positive_negative() {
    let numbers = vec![-5.0, 0.0, 5.0];
    let result = calculate_average(&numbers);
    assert_eq!(result, Ok(0.0));
}

#[test]
fn test_calculate_average_with_decimals() {
    let numbers = vec![1.5, 2.5, 3.0];
    let result = calculate_average(&numbers);
    assert!(result.is_ok());
    let avg = result.unwrap();
    // 7.0 / 3 = 2.333... (account for floating-point precision)
    assert!((avg - (7.0 / 3.0)).abs() < 1e-10);
}

#[test]
fn test_calculate_average_empty_slice() {
    let numbers: Vec<f64> = vec![];
    let result = calculate_average(&numbers);
    assert_eq!(
        result,
        Err("Input must be a non-empty slice".to_string())
    );
}

#[test]
fn test_calculate_average_very_small_numbers() {
    let numbers = vec![0.000001, 0.000002, 0.000003];
    let result = calculate_average(&numbers);
    assert!(result.is_ok());
    assert!(
        (result.unwrap() - 0.000002).abs() < 1e-10,
        "Average should be approximately 0.000002"
    );
}

#[test]
fn test_calculate_average_infinity_propagation() {
    let numbers = vec![f64::INFINITY, 1.0];
    let result = calculate_average(&numbers);
    assert!(result.is_ok());
    assert!(result.unwrap().is_infinite());
}

// ============================================================================
// Tests for fizzbuzz
// ============================================================================

#[test]
fn test_fizzbuzz_returns_number_as_string() {
    assert_eq!(fizzbuzz(1), "1");
    assert_eq!(fizzbuzz(2), "2");
    assert_eq!(fizzbuzz(4), "4");
    assert_eq!(fizzbuzz(7), "7");
}

#[test]
fn test_fizzbuzz_returns_fizz_for_multiples_of_3() {
    assert_eq!(fizzbuzz(3), "fizz");
    assert_eq!(fizzbuzz(6), "fizz");
    assert_eq!(fizzbuzz(9), "fizz");
    assert_eq!(fizzbuzz(12), "fizz");
    assert_eq!(fizzbuzz(18), "fizz");
}

#[test]
fn test_fizzbuzz_returns_buzz_for_multiples_of_5() {
    assert_eq!(fizzbuzz(5), "buzz");
    assert_eq!(fizzbuzz(10), "buzz");
    assert_eq!(fizzbuzz(20), "buzz");
    assert_eq!(fizzbuzz(25), "buzz");
}

#[test]
fn test_fizzbuzz_returns_fizzbuzz_for_multiples_of_15() {
    assert_eq!(fizzbuzz(15), "fizzbuzz");
    assert_eq!(fizzbuzz(30), "fizzbuzz");
    assert_eq!(fizzbuzz(45), "fizzbuzz");
    assert_eq!(fizzbuzz(60), "fizzbuzz");
    assert_eq!(fizzbuzz(75), "fizzbuzz");
}

#[test]
fn test_fizzbuzz_zero() {
    // 0 is a multiple of both 3 and 5
    assert_eq!(fizzbuzz(0), "fizzbuzz");
}

#[test]
fn test_fizzbuzz_large_multiples() {
    assert_eq!(fizzbuzz(999), "fizz"); // 999 % 3 == 0
    assert_eq!(fizzbuzz(1000), "buzz"); // 1000 % 5 == 0
    assert_eq!(fizzbuzz(10005), "fizzbuzz"); // 10005 % 15 == 0
}

#[test]
fn test_fizzbuzz_sequence() {
    let expected = vec![
        "1", "2", "fizz", "4", "buzz", "fizz", "7", "8", "fizz", "buzz",
        "11", "fizz", "13", "14", "fizzbuzz",
    ];
    for (i, expected_str) in expected.iter().enumerate() {
        let n = (i + 1) as u32;
        assert_eq!(
            fizzbuzz(n),
            expected_str.to_string(),
            "Failed at n={}",
            n
        );
    }
}

#[test]
fn test_fizzbuzz_u32_max() {
    // u32::MAX = 4,294,967,295
    // 4,294,967,295 % 3 = 0 (divisible by 3)
    // 4,294,967,295 % 5 = 0 (divisible by 5)
    assert_eq!(fizzbuzz(u32::MAX), "fizzbuzz");
}

// ============================================================================
// Tests for reverse_words
// ============================================================================

#[test]
fn test_reverse_words_simple() {
    assert_eq!(reverse_words("hello world"), "world hello");
}

#[test]
fn test_reverse_words_three_words() {
    assert_eq!(
        reverse_words("one two three"),
        "three two one"
    );
}

#[test]
fn test_reverse_words_single_word() {
    assert_eq!(reverse_words("hello"), "hello");
}

#[test]
fn test_reverse_words_empty_string() {
    assert_eq!(reverse_words(""), "");
}

#[test]
fn test_reverse_words_whitespace_only() {
    assert_eq!(reverse_words("   "), "");
}

#[test]
fn test_reverse_words_multiple_spaces_between_words() {
    // split_whitespace handles multiple spaces
    assert_eq!(reverse_words("hello  world"), "world hello");
    assert_eq!(reverse_words("one   two    three"), "three two one");
}

#[test]
fn test_reverse_words_leading_and_trailing_spaces() {
    assert_eq!(reverse_words("  hello world  "), "world hello");
}

#[test]
fn test_reverse_words_tabs_and_newlines() {
    assert_eq!(reverse_words("hello\tworld"), "world hello");
    assert_eq!(reverse_words("hello\nworld"), "world hello");
}

#[test]
fn test_reverse_words_long_sentence() {
    assert_eq!(
        reverse_words("the quick brown fox jumps over the lazy dog"),
        "dog lazy the over jumps fox brown quick the"
    );
}

#[test]
fn test_reverse_words_with_punctuation() {
    assert_eq!(
        reverse_words("hello, world!"),
        "world! hello,"
    );
}

#[test]
fn test_reverse_words_unicode_characters() {
    assert_eq!(reverse_words("café naïve"), "naïve café");
    assert_eq!(reverse_words("🦀 rust 🎉"), "🎉 rust 🦀");
}

#[test]
fn test_reverse_words_mixed_whitespace() {
    assert_eq!(reverse_words("a\t  \nb  \n  c"), "c b a");
}

#[test]
fn test_reverse_words_single_character_words() {
    assert_eq!(reverse_words("a b c d e"), "e d c b a");
}
