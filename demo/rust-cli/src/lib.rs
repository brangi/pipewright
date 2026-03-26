// Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
// SPDX-License-Identifier: MIT

//! Text processing utilities for the pipewright Rust demo.

/// Count the frequency of each word in the given text.
/// Words are lowercased and split on whitespace.
pub fn word_frequency(text: &str) -> std::collections::HashMap<String, usize> {
    let mut freq = std::collections::HashMap::new();
    for word in text.split_whitespace() {
        let cleaned: String = word
            .chars()
            .filter(|c| c.is_alphanumeric())
            .collect::<String>()
            .to_lowercase();
        if !cleaned.is_empty() {
            *freq.entry(cleaned).or_insert(0) += 1;
        }
    }
    freq
}

/// Truncate a string to the given max length, adding "..." if truncated.
pub fn truncate(text: &str, max_len: usize) -> String {
    if text.len() <= max_len {
        return text.to_string();
    }
    if max_len <= 3 {
        return ".".repeat(max_len);
    }
    format!("{}...", &text[..max_len - 3])
}

/// Convert a string to title case (first letter of each word capitalized).
pub fn title_case(text: &str) -> String {
    text.split_whitespace()
        .map(|word| {
            let mut chars = word.chars();
            match chars.next() {
                None => String::new(),
                Some(first) => {
                    let upper: String = first.to_uppercase().collect();
                    upper + &chars.as_str().to_lowercase()
                }
            }
        })
        .collect::<Vec<_>>()
        .join(" ")
}

/// Check if a string is a valid identifier (alphanumeric + underscore, not starting with digit).
pub fn is_valid_identifier(name: &str) -> bool {
    if name.is_empty() {
        return false;
    }
    let mut chars = name.chars();
    let first = chars.next().unwrap();
    if !first.is_alphabetic() && first != '_' {
        return false;
    }
    chars.all(|c| c.is_alphanumeric() || c == '_')
}
