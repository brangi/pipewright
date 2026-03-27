// Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
// SPDX-License-Identifier: MIT

//! Text processing utilities for the pipewright Rust demo.
//!
//! This library provides a small set of general-purpose text manipulation
//! functions used by the `textool` CLI binary (`src/main.rs`). It is also
//! part of the pipewright multi-language showcase, demonstrating how
//! pipewright workflows (`test-gen`, `code-review`, `docs-gen`) operate on
//! Rust source code.
//!
//! # Functions
//!
//! | Function | Description |
//! |---|---|
//! | [`word_frequency`] | Count how often each word appears in a string |
//! | [`truncate`] | Shorten a string to a maximum length with an ellipsis |
//! | [`title_case`] | Capitalise the first letter of every word |
//! | [`is_valid_identifier`] | Check whether a string is a legal identifier name |
//!
//! # Quick-start
//!
//! ```rust
//! use pipewright_rust_demo::{word_frequency, truncate, title_case, is_valid_identifier};
//!
//! // Count words (case-insensitive, punctuation stripped)
//! let freq = word_frequency("hello world hello");
//! assert_eq!(freq["hello"], 2);
//!
//! // Truncate long lines for display
//! assert_eq!(truncate("Hello, World!", 8), "Hello...");
//!
//! // Normalise headings to title case
//! assert_eq!(title_case("the quick brown fox"), "The Quick Brown Fox");
//!
//! // Validate user-supplied symbol names
//! assert!(is_valid_identifier("my_var"));
//! assert!(!is_valid_identifier("2bad"));
//! ```

/// Count the frequency of each word in the given text.
///
/// Words are split on whitespace, lowercased, and stripped of all
/// non-alphanumeric characters before counting, so punctuation does not
/// affect the result (`"hello,"` and `"hello"` are the same word). Tokens
/// that reduce to an empty string after cleaning are silently ignored.
///
/// # Arguments
///
/// * `text` - The input string to analyse. May be empty.
///
/// # Returns
///
/// A [`HashMap`](std::collections::HashMap) mapping each unique lowercased
/// word to its occurrence count. Returns an empty map when `text` contains
/// no word characters.
///
/// # Examples
///
/// ```rust
/// use pipewright_rust_demo::word_frequency;
///
/// let freq = word_frequency("Rust is fast. Rust is safe.");
/// assert_eq!(freq["rust"], 2);
/// assert_eq!(freq["fast"], 1);
///
/// // Punctuation is stripped
/// let freq2 = word_frequency("hello, hello!");
/// assert_eq!(freq2["hello"], 2);
///
/// // Empty input produces an empty map
/// assert!(word_frequency("").is_empty());
/// ```
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

/// Truncate a string to the given maximum byte length, appending `"..."` when
/// the string is shortened.
///
/// Truncation uses Rust's byte-slice syntax (`&text[..n]`), so `max_len`
/// must fall on a valid UTF-8 character boundary. For ASCII text this is
/// always safe; for multibyte text callers should ensure `max_len` does not
/// split a code point.
///
/// **Special case:** when `max_len` ≤ 3, the return value is `max_len` dots
/// (`"."` × `max_len`) rather than trying to fit the ellipsis inside the budget.
///
/// # Arguments
///
/// * `text`    - The string to potentially truncate.
/// * `max_len` - Maximum number of bytes in the returned string (inclusive of
///               the `"..."` suffix when truncation occurs).
///
/// # Returns
///
/// * The original `text` as a [`String`] if its byte length ≤ `max_len`.
/// * A truncated string ending in `"..."` of total length `max_len` when the
///   original is longer.
/// * A string of `max_len` dots when `max_len` ≤ 3.
///
/// # Examples
///
/// ```rust
/// use pipewright_rust_demo::truncate;
///
/// assert_eq!(truncate("Hi", 10),           "Hi");          // short enough
/// assert_eq!(truncate("Hello, World!", 8), "Hello...");    // truncated
/// assert_eq!(truncate("Hello", 3),         "...");         // edge: max_len == 3
/// assert_eq!(truncate("Hello", 2),         "..");          // edge: max_len < 3
/// ```
pub fn truncate(text: &str, max_len: usize) -> String {
    if text.len() <= max_len {
        return text.to_string();
    }
    if max_len <= 3 {
        return ".".repeat(max_len);
    }
    format!("{}...", &text[..max_len - 3])
}

/// Convert a string to title case, capitalising the first letter of every
/// whitespace-delimited word and lowercasing the remainder.
///
/// Words are identified via [`str::split_whitespace`], so leading/trailing
/// whitespace is not preserved in the output and multiple interior spaces are
/// collapsed to a single space (words are re-joined with `" "`).
///
/// # Arguments
///
/// * `text` - The input string to convert. May be empty or contain any
///   Unicode characters.
///
/// # Returns
///
/// A new [`String`] in title case. Returns an empty string when `text` is
/// empty or consists entirely of whitespace.
///
/// # Examples
///
/// ```rust
/// use pipewright_rust_demo::title_case;
///
/// assert_eq!(title_case("the quick brown fox"), "The Quick Brown Fox");
/// assert_eq!(title_case("RUST LANG"),           "Rust Lang");
/// assert_eq!(title_case("single"),              "Single");
/// assert_eq!(title_case(""),                    "");
///
/// // Interior whitespace is collapsed
/// assert_eq!(title_case("  hello   world  "),   "Hello World");
/// ```
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

/// Check whether a string is a valid programming-language identifier.
///
/// A valid identifier satisfies all of the following rules:
///
/// 1. It is **non-empty**.
/// 2. Its **first character** is either an alphabetic Unicode scalar
///    (`char::is_alphabetic`) or an underscore (`'_'`).
/// 3. Every **subsequent character** is alphanumeric (`char::is_alphanumeric`)
///    or an underscore.
///
/// This matches the identifier rules used by most C-family languages (C, C++,
/// Rust, Python, JavaScript) and many configuration formats.
///
/// # Arguments
///
/// * `name` - The string to validate.
///
/// # Returns
///
/// `true` if `name` satisfies all identifier rules; `false` otherwise.
///
/// # Examples
///
/// ```rust
/// use pipewright_rust_demo::is_valid_identifier;
///
/// // Valid identifiers
/// assert!(is_valid_identifier("foo"));
/// assert!(is_valid_identifier("_bar"));
/// assert!(is_valid_identifier("CamelCase"));
/// assert!(is_valid_identifier("x1"));
/// assert!(is_valid_identifier("__dunder__"));
///
/// // Invalid identifiers
/// assert!(!is_valid_identifier(""));           // empty
/// assert!(!is_valid_identifier("2fast"));      // starts with digit
/// assert!(!is_valid_identifier("has-hyphen")); // hyphen not allowed
/// assert!(!is_valid_identifier("has space"));  // space not allowed
/// ```
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

#[cfg(test)]
mod tests {
    use super::*;

    // ============================================================================
    // word_frequency tests
    // ============================================================================

    #[test]
    fn word_frequency_simple_text() {
        let text = "hello world hello";
        let result = word_frequency(text);
        assert_eq!(result.get("hello"), Some(&2));
        assert_eq!(result.get("world"), Some(&1));
        assert_eq!(result.len(), 2);
    }

    #[test]
    fn word_frequency_case_insensitive() {
        let text = "Hello HELLO hello";
        let result = word_frequency(text);
        assert_eq!(result.get("hello"), Some(&3));
        assert_eq!(result.len(), 1);
    }

    #[test]
    fn word_frequency_strips_punctuation() {
        let text = "hello, world! hello.";
        let result = word_frequency(text);
        assert_eq!(result.get("hello"), Some(&2));
        assert_eq!(result.get("world"), Some(&1));
        assert_eq!(result.contains_key(","), false);
        assert_eq!(result.contains_key("!"), false);
    }

    #[test]
    fn word_frequency_mixed_alphanumeric() {
        let text = "test123 TEST123 test456";
        let result = word_frequency(text);
        assert_eq!(result.get("test123"), Some(&2));
        assert_eq!(result.get("test456"), Some(&1));
    }

    #[test]
    fn word_frequency_empty_string() {
        let text = "";
        let result = word_frequency(text);
        assert_eq!(result.len(), 0);
    }

    #[test]
    fn word_frequency_whitespace_only() {
        let text = "   \t\n   ";
        let result = word_frequency(text);
        assert_eq!(result.len(), 0);
    }

    #[test]
    fn word_frequency_punctuation_only() {
        let text = "!!! ??? ...";
        let result = word_frequency(text);
        assert_eq!(result.len(), 0);
    }

    #[test]
    fn word_frequency_single_word() {
        let text = "hello";
        let result = word_frequency(text);
        assert_eq!(result.get("hello"), Some(&1));
        assert_eq!(result.len(), 1);
    }

    #[test]
    fn word_frequency_multiple_spaces() {
        let text = "hello    world";
        let result = word_frequency(text);
        assert_eq!(result.get("hello"), Some(&1));
        assert_eq!(result.get("world"), Some(&1));
        assert_eq!(result.len(), 2);
    }

    #[test]
    fn word_frequency_complex_punctuation() {
        let text = "It's a test-case with hyphens, semicolons; and more!";
        let result = word_frequency(text);
        assert_eq!(result.get("its"), Some(&1));
        assert_eq!(result.get("a"), Some(&1));
        assert_eq!(result.get("testcase"), Some(&1));
        assert_eq!(result.get("with"), Some(&1));
        // "test-case" becomes "testcase" after filtering (hyphen is removed, not split)
    }

    // ============================================================================
    // truncate tests
    // ============================================================================

    #[test]
    fn truncate_no_truncation_needed() {
        let text = "hello";
        let result = truncate(text, 10);
        assert_eq!(result, "hello");
    }

    #[test]
    fn truncate_exact_length() {
        let text = "hello";
        let result = truncate(text, 5);
        assert_eq!(result, "hello");
    }

    #[test]
    fn truncate_longer_than_max() {
        let text = "hello world";
        let result = truncate(text, 8);
        assert_eq!(result, "hello...");
        assert_eq!(result.len(), 8);
    }

    #[test]
    fn truncate_single_char_max() {
        let text = "hello";
        let result = truncate(text, 1);
        assert_eq!(result, ".");
    }

    #[test]
    fn truncate_two_char_max() {
        let text = "hello";
        let result = truncate(text, 2);
        assert_eq!(result, "..");
    }

    #[test]
    fn truncate_three_char_max() {
        let text = "hello";
        let result = truncate(text, 3);
        assert_eq!(result, "...");
    }

    #[test]
    fn truncate_four_char_max() {
        let text = "hello";
        let result = truncate(text, 4);
        assert_eq!(result, "h...");
        assert_eq!(result.len(), 4);
    }

    #[test]
    fn truncate_empty_string() {
        let text = "";
        let result = truncate(text, 5);
        assert_eq!(result, "");
    }

    #[test]
    fn truncate_unicode_aware() {
        // Rust uses byte length, so this tests edge case behavior
        let text = "hello world longer";
        let result = truncate(text, 10);
        assert_eq!(result.len(), 10);
        assert!(result.ends_with("..."));
    }

    #[test]
    fn truncate_large_max_length() {
        let text = "short";
        let result = truncate(text, 1000);
        assert_eq!(result, "short");
    }

    // ============================================================================
    // title_case tests
    // ============================================================================

    #[test]
    fn title_case_simple() {
        let text = "hello world";
        let result = title_case(text);
        assert_eq!(result, "Hello World");
    }

    #[test]
    fn title_case_already_titled() {
        let text = "Hello World";
        let result = title_case(text);
        assert_eq!(result, "Hello World");
    }

    #[test]
    fn title_case_all_caps() {
        let text = "HELLO WORLD";
        let result = title_case(text);
        assert_eq!(result, "Hello World");
    }

    #[test]
    fn title_case_mixed_case() {
        let text = "hELLO wORLD";
        let result = title_case(text);
        assert_eq!(result, "Hello World");
    }

    #[test]
    fn title_case_single_word() {
        let text = "hello";
        let result = title_case(text);
        assert_eq!(result, "Hello");
    }

    #[test]
    fn title_case_empty_string() {
        let text = "";
        let result = title_case(text);
        assert_eq!(result, "");
    }

    #[test]
    fn title_case_whitespace_only() {
        let text = "   ";
        let result = title_case(text);
        assert_eq!(result, "");
    }

    #[test]
    fn title_case_multiple_spaces() {
        let text = "hello    world";
        let result = title_case(text);
        assert_eq!(result, "Hello World");
    }

    #[test]
    fn title_case_numbers() {
        let text = "hello 123 world";
        let result = title_case(text);
        assert_eq!(result, "Hello 123 World");
    }

    #[test]
    fn title_case_special_characters() {
        let text = "hello! @world #test";
        let result = title_case(text);
        // Special chars stay as-is since split_whitespace is used
        assert_eq!(result, "Hello! @world #test");
    }

    #[test]
    fn title_case_punctuation_at_start() {
        let text = "'hello 'world";
        let result = title_case(text);
        // Single quotes and subsequent chars are treated literally
        assert_eq!(result, "'hello 'world");
    }

    // ============================================================================
    // is_valid_identifier tests
    // ============================================================================

    #[test]
    fn is_valid_identifier_simple_valid() {
        assert!(is_valid_identifier("hello"));
    }

    #[test]
    fn is_valid_identifier_with_underscore() {
        assert!(is_valid_identifier("_hello"));
    }

    #[test]
    fn is_valid_identifier_with_numbers() {
        assert!(is_valid_identifier("hello123"));
    }

    #[test]
    fn is_valid_identifier_underscore_prefix() {
        assert!(is_valid_identifier("_"));
    }

    #[test]
    fn is_valid_identifier_multiple_underscores() {
        assert!(is_valid_identifier("__hello__"));
    }

    #[test]
    fn is_valid_identifier_snake_case() {
        assert!(is_valid_identifier("hello_world_123"));
    }

    #[test]
    fn is_valid_identifier_single_letter() {
        assert!(is_valid_identifier("a"));
    }

    #[test]
    fn is_valid_identifier_single_underscore() {
        assert!(is_valid_identifier("_"));
    }

    #[test]
    fn is_valid_identifier_caps() {
        assert!(is_valid_identifier("HELLO"));
    }

    #[test]
    fn is_valid_identifier_mixed_case() {
        assert!(is_valid_identifier("HelloWorld"));
    }

    #[test]
    fn is_valid_identifier_empty_string() {
        assert!(!is_valid_identifier(""));
    }

    #[test]
    fn is_valid_identifier_starts_with_digit() {
        assert!(!is_valid_identifier("123hello"));
    }

    #[test]
    fn is_valid_identifier_starts_with_special_char() {
        assert!(!is_valid_identifier("@hello"));
    }

    #[test]
    fn is_valid_identifier_contains_space() {
        assert!(!is_valid_identifier("hello world"));
    }

    #[test]
    fn is_valid_identifier_contains_dash() {
        assert!(!is_valid_identifier("hello-world"));
    }

    #[test]
    fn is_valid_identifier_contains_dot() {
        assert!(!is_valid_identifier("hello.world"));
    }

    #[test]
    fn is_valid_identifier_contains_punctuation() {
        assert!(!is_valid_identifier("hello!"));
    }

    #[test]
    fn is_valid_identifier_special_chars() {
        assert!(!is_valid_identifier("hello$world"));
    }

    #[test]
    fn is_valid_identifier_digit_not_first() {
        assert!(is_valid_identifier("h3ll0"));
    }

    #[test]
    fn is_valid_identifier_long_valid_name() {
        assert!(is_valid_identifier("very_long_identifier_name_with_underscores_123"));
    }
}
