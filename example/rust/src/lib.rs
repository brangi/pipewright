// Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
// SPDX-License-Identifier: MIT

//! Simple utility functions for testing pipewright's test-gen workflow.

/// Calculate the average of a slice of numbers.
///
/// Returns an error if the slice is empty.
pub fn calculate_average(numbers: &[f64]) -> Result<f64, String> {
    if numbers.is_empty() {
        return Err("Input must be a non-empty slice".to_string());
    }
    let total: f64 = numbers.iter().sum();
    Ok(total / numbers.len() as f64)
}

/// Return "fizz", "buzz", "fizzbuzz", or the number as a string.
pub fn fizzbuzz(n: u32) -> String {
    match (n % 3, n % 5) {
        (0, 0) => "fizzbuzz".to_string(),
        (0, _) => "fizz".to_string(),
        (_, 0) => "buzz".to_string(),
        _ => n.to_string(),
    }
}

/// Reverse the order of words in a sentence.
pub fn reverse_words(sentence: &str) -> String {
    sentence
        .split_whitespace()
        .rev()
        .collect::<Vec<&str>>()
        .join(" ")
}
