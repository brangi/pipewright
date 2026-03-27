// Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
// SPDX-License-Identifier: MIT

package main

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
	"time"
)

// TestHandleHealth tests the HandleHealth HTTP handler
func TestHandleHealth(t *testing.T) {
	tests := []struct {
		name           string
		method         string
		wantStatusCode int
		wantContentType string
	}{
		{
			name:            "GET request returns ok status",
			method:          "GET",
			wantStatusCode:  http.StatusOK,
			wantContentType: "application/json",
		},
		{
			name:            "POST request returns ok status",
			method:          "POST",
			wantStatusCode:  http.StatusOK,
			wantContentType: "application/json",
		},
		{
			name:            "HEAD request returns ok status",
			method:          "HEAD",
			wantStatusCode:  http.StatusOK,
			wantContentType: "application/json",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Create a new request with the specified method
			req := httptest.NewRequest(tt.method, "/health", nil)
			// Create a ResponseWriter to record the response
			w := httptest.NewRecorder()

			// Call the handler
			HandleHealth(w, req)

			// Check status code
			if w.Code != tt.wantStatusCode {
				t.Errorf("HandleHealth() status = %v, want %v", w.Code, tt.wantStatusCode)
			}

			// Check Content-Type header
			contentType := w.Header().Get("Content-Type")
			if contentType != tt.wantContentType {
				t.Errorf("HandleHealth() Content-Type = %q, want %q", contentType, tt.wantContentType)
			}

			// Parse and validate response body
			var resp HealthResponse
			err := json.Unmarshal(w.Body.Bytes(), &resp)
			if err != nil {
				t.Errorf("HandleHealth() failed to unmarshal response: %v", err)
				return
			}

			// Check status field
			if resp.Status != "ok" {
				t.Errorf("HandleHealth() Status = %q, want %q", resp.Status, "ok")
			}

			// Check that timestamp is a valid RFC3339 format
			_, err = time.Parse(time.RFC3339, resp.Timestamp)
			if err != nil {
				t.Errorf("HandleHealth() Timestamp %q is not valid RFC3339: %v", resp.Timestamp, err)
			}

			// Check that timestamp is recent (within last 5 seconds)
			parsedTime, _ := time.Parse(time.RFC3339, resp.Timestamp)
			if time.Since(parsedTime) > 5*time.Second {
				t.Errorf("HandleHealth() Timestamp is too old: %v", resp.Timestamp)
			}
		})
	}
}

// TestHandleHealthResponseStructure validates the response JSON structure
func TestHandleHealthResponseStructure(t *testing.T) {
	req := httptest.NewRequest("GET", "/health", nil)
	w := httptest.NewRecorder()

	HandleHealth(w, req)

	// Verify the response is valid JSON with expected fields
	body := w.Body.String()
	if !strings.Contains(body, "\"status\"") {
		t.Error("HandleHealth() response missing 'status' field")
	}
	if !strings.Contains(body, "\"timestamp\"") {
		t.Error("HandleHealth() response missing 'timestamp' field")
	}
	if !strings.Contains(body, "\"ok\"") {
		t.Error("HandleHealth() response missing 'ok' status value")
	}
}

// TestCountWords tests the CountWords function with various inputs
func TestCountWords(t *testing.T) {
	tests := []struct {
		name     string
		input    string
		expected int
	}{
		// Happy paths - Normal cases
		{
			name:     "single word",
			input:    "hello",
			expected: 1,
		},
		{
			name:     "two words",
			input:    "hello world",
			expected: 2,
		},
		{
			name:     "multiple words",
			input:    "the quick brown fox jumps",
			expected: 5,
		},
		{
			name:     "sentence with punctuation",
			input:    "hello, world!",
			expected: 2,
		},
		{
			name:     "words with numbers",
			input:    "test 123 sample 456",
			expected: 4,
		},
		// Edge cases - Whitespace variations
		{
			name:     "empty string",
			input:    "",
			expected: 0,
		},
		{
			name:     "only spaces",
			input:    "   ",
			expected: 0,
		},
		{
			name:     "leading spaces",
			input:    "   hello world",
			expected: 2,
		},
		{
			name:     "trailing spaces",
			input:    "hello world   ",
			expected: 2,
		},
		{
			name:     "multiple spaces between words",
			input:    "hello    world",
			expected: 2,
		},
		{
			name:     "tabs and newlines",
			input:    "hello\t\nworld",
			expected: 2,
		},
		{
			name:     "mixed whitespace",
			input:    "  one  \t two  \n three  ",
			expected: 3,
		},
		// Edge cases - Special content
		{
			name:     "single space",
			input:    " ",
			expected: 0,
		},
		{
			name:     "long word",
			input:    "supercalifragilisticexpialidocious",
			expected: 1,
		},
		{
			name:     "words with hyphens",
			input:    "well-known open-source",
			expected: 2,
		},
		{
			name:     "many single char words",
			input:    "a b c d e f",
			expected: 6,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := CountWords(tt.input)
			if result != tt.expected {
				t.Errorf("CountWords(%q) = %d, want %d", tt.input, result, tt.expected)
			}
		})
	}
}

// TestIsPalindrome tests the IsPalindrome function with various inputs
func TestIsPalindrome(t *testing.T) {
	tests := []struct {
		name     string
		input    string
		expected bool
	}{
		// Happy paths - Valid palindromes
		{
			name:     "simple palindrome",
			input:    "racecar",
			expected: true,
		},
		{
			name:     "single character",
			input:    "a",
			expected: true,
		},
		{
			name:     "two same characters",
			input:    "aa",
			expected: true,
		},
		{
			name:     "two different characters",
			input:    "ab",
			expected: false,
		},
		{
			name:     "palindrome with spaces and punctuation",
			input:    "A man, a plan, a canal: Panama",
			expected: true,
		},
		{
			name:     "palindrome with mixed case",
			input:    "Madam",
			expected: true,
		},
		{
			name:     "palindrome with numbers",
			input:    "12321",
			expected: true,
		},
		{
			name:     "palindrome ignoring punctuation",
			input:    "Was it a car or a cat I saw?",
			expected: true,
		},
		{
			name:     "complex palindrome",
			input:    "Do geese see God?",
			expected: true,
		},
		// Edge cases - Non-palindromes
		{
			name:     "simple non-palindrome",
			input:    "hello",
			expected: false,
		},
		{
			name:     "word with spaces",
			input:    "hello world",
			expected: false,
		},
		{
			name:     "numbers non-palindrome",
			input:    "12345",
			expected: false,
		},
		// Edge cases - Special cases
		{
			name:     "empty string",
			input:    "",
			expected: true,
		},
		{
			name:     "only spaces",
			input:    "   ",
			expected: true,
		},
		{
			name:     "only punctuation",
			input:    "!!!",
			expected: true,
		},
		{
			name:     "mixed special characters",
			input:    "!@#@!",
			expected: true,
		},
		{
			name:     "single special character",
			input:    "!",
			expected: true,
		},
		{
			name:     "number palindrome with special chars",
			input:    "1-2-1",
			expected: true,
		},
		{
			name:     "case insensitive check",
			input:    "ABA",
			expected: true,
		},
		{
			name:     "lowercase palindrome",
			input:    "aba",
			expected: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := IsPalindrome(tt.input)
			if result != tt.expected {
				t.Errorf("IsPalindrome(%q) = %v, want %v", tt.input, result, tt.expected)
			}
		})
	}
}

// TestCamelToSnake tests the CamelToSnake function with various inputs
func TestCamelToSnake(t *testing.T) {
	tests := []struct {
		name     string
		input    string
		expected string
	}{
		// Happy paths - Standard camelCase
		{
			name:     "simple camelCase",
			input:    "camelCase",
			expected: "camel_case",
		},
		{
			name:     "camelCaseWithMultipleWords",
			input:    "camelCaseWithMultipleWords",
			expected: "camel_case_with_multiple_words",
		},
		{
			name:     "handleHTTPRequest",
			input:    "handleHTTPRequest",
			expected: "handle_h_t_t_p_request",
		},
		{
			name:     "single word lowercase",
			input:    "hello",
			expected: "hello",
		},
		// Edge cases - Already snake_case or variations
		{
			name:     "already snake_case",
			input:    "snake_case",
			expected: "snake_case",
		},
		{
			name:     "PascalCase",
			input:    "PascalCase",
			expected: "pascal_case",
		},
		{
			name:     "UPPERCASE",
			input:    "UPPERCASE",
			expected: "u_p_p_e_r_c_a_s_e",
		},
		{
			name:     "empty string",
			input:    "",
			expected: "",
		},
		{
			name:     "single character lowercase",
			input:    "a",
			expected: "a",
		},
		{
			name:     "single character uppercase",
			input:    "A",
			expected: "a",
		},
		{
			name:     "two uppercase letters",
			input:    "AB",
			expected: "a_b",
		},
		{
			name:     "camelCaseWithNumbers",
			input:    "camelCase123WithNumbers",
			expected: "camel_case123_with_numbers",
		},
		{
			name:     "consecutive uppercase letters",
			input:    "getHTTPResponseCode",
			expected: "get_h_t_t_p_response_code",
		},
		{
			name:     "number at start",
			input:    "123camelCase",
			expected: "123camel_case",
		},
		{
			name:     "HTTPServer",
			input:    "HTTPServer",
			expected: "h_t_t_p_server",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := CamelToSnake(tt.input)
			if result != tt.expected {
				t.Errorf("CamelToSnake(%q) = %q, want %q", tt.input, result, tt.expected)
			}
		})
	}
}

// TestFormatBytes tests the FormatBytes function with various inputs
func TestFormatBytes(t *testing.T) {
	tests := []struct {
		name     string
		input    int64
		expected string
	}{
		// Happy paths - Standard byte sizes
		{
			name:     "single byte",
			input:    1,
			expected: "1 B",
		},
		{
			name:     "10 bytes",
			input:    10,
			expected: "10 B",
		},
		{
			name:     "100 bytes",
			input:    100,
			expected: "100 B",
		},
		{
			name:     "512 bytes",
			input:    512,
			expected: "512 B",
		},
		{
			name:     "1 kilobyte",
			input:    1024,
			expected: "1.0 KB",
		},
		{
			name:     "1.5 kilobytes",
			input:    1536,
			expected: "1.5 KB",
		},
		{
			name:     "10 kilobytes",
			input:    10 * 1024,
			expected: "10.0 KB",
		},
		{
			name:     "100 kilobytes",
			input:    100 * 1024,
			expected: "100.0 KB",
		},
		{
			name:     "512 kilobytes",
			input:    512 * 1024,
			expected: "512.0 KB",
		},
		{
			name:     "1 megabyte",
			input:    1024 * 1024,
			expected: "1.0 MB",
		},
		{
			name:     "1.5 megabytes",
			input:    1536 * 1024,
			expected: "1.5 MB",
		},
		{
			name:     "10 megabytes",
			input:    10 * 1024 * 1024,
			expected: "10.0 MB",
		},
		{
			name:     "100 megabytes",
			input:    100 * 1024 * 1024,
			expected: "100.0 MB",
		},
		{
			name:     "500 megabytes",
			input:    500 * 1024 * 1024,
			expected: "500.0 MB",
		},
		{
			name:     "1 gigabyte",
			input:    1024 * 1024 * 1024,
			expected: "1.0 GB",
		},
		{
			name:     "2.5 gigabytes",
			input:    int64(2.5 * 1024 * 1024 * 1024),
			expected: "2.5 GB",
		},
		{
			name:     "10 gigabytes",
			input:    10 * 1024 * 1024 * 1024,
			expected: "10.0 GB",
		},
		{
			name:     "100 gigabytes",
			input:    100 * 1024 * 1024 * 1024,
			expected: "100.0 GB",
		},
		// Edge cases
		{
			name:     "zero bytes",
			input:    0,
			expected: "0 B",
		},
		{
			name:     "just below 1 KB",
			input:    1023,
			expected: "1023 B",
		},
		{
			name:     "just at 1 KB boundary",
			input:    1024,
			expected: "1.0 KB",
		},
		{
			name:     "just above 1 KB",
			input:    1025,
			expected: "1.0 KB",
		},
		{
			name:     "just below 1 MB",
			input:    (1024 * 1024) - 1,
			expected: "1024.0 KB",
		},
		{
			name:     "just at 1 MB boundary",
			input:    1024 * 1024,
			expected: "1.0 MB",
		},
		{
			name:     "just above 1 MB",
			input:    (1024 * 1024) + 1,
			expected: "1.0 MB",
		},
		{
			name:     "just below 1 GB",
			input:    (1024 * 1024 * 1024) - 1,
			expected: "1024.0 MB",
		},
		{
			name:     "just at 1 GB boundary",
			input:    1024 * 1024 * 1024,
			expected: "1.0 GB",
		},
		{
			name:     "very large size",
			input:    1000 * 1024 * 1024 * 1024,
			expected: "1000.0 GB",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := FormatBytes(tt.input)
			if result != tt.expected {
				t.Errorf("FormatBytes(%d) = %q, want %q", tt.input, result, tt.expected)
			}
		})
	}
}

// TestFormatBytesFormatting verifies the formatting precision
func TestFormatBytesFormatting(t *testing.T) {
	tests := []struct {
		name           string
		input          int64
		shouldContain  string
	}{
		{
			name:          "KB formatting has decimal point",
			input:         1024,
			shouldContain: " KB",
		},
		{
			name:          "MB formatting has decimal point",
			input:         1024 * 1024,
			shouldContain: " MB",
		},
		{
			name:          "GB formatting has decimal point",
			input:         1024 * 1024 * 1024,
			shouldContain: " GB",
		},
		{
			name:          "bytes use B suffix",
			input:         512,
			shouldContain: " B",
		},
		{
			name:          "fractional KB shows decimal",
			input:         1536,
			shouldContain: ".5 KB",
		},
		{
			name:          "fractional MB shows decimal",
			input:         1536 * 1024,
			shouldContain: ".5 MB",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := FormatBytes(tt.input)
			if !strings.Contains(result, tt.shouldContain) {
				t.Errorf("FormatBytes(%d) = %q, should contain %q", tt.input, result, tt.shouldContain)
			}
		})
	}
}

// BenchmarkCountWords benchmarks the CountWords function
func BenchmarkCountWords(b *testing.B) {
	text := "the quick brown fox jumps over the lazy dog"
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		CountWords(text)
	}
}

// BenchmarkIsPalindrome benchmarks the IsPalindrome function
func BenchmarkIsPalindrome(b *testing.B) {
	text := "A man, a plan, a canal: Panama"
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		IsPalindrome(text)
	}
}

// BenchmarkCamelToSnake benchmarks the CamelToSnake function
func BenchmarkCamelToSnake(b *testing.B) {
	text := "camelCaseWithMultipleWords"
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		CamelToSnake(text)
	}
}

// BenchmarkFormatBytes benchmarks the FormatBytes function
func BenchmarkFormatBytes(b *testing.B) {
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		FormatBytes(1024 * 1024)
	}
}
