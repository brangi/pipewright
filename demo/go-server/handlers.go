// Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
// SPDX-License-Identifier: MIT

// Package main provides HTTP handlers for the pipewright Go demo.
package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"strings"
	"time"
	"unicode"
)

// HealthResponse represents the health check response.
type HealthResponse struct {
	Status    string `json:"status"`
	Timestamp string `json:"timestamp"`
}

// HandleHealth returns a health check response.
func HandleHealth(w http.ResponseWriter, r *http.Request) {
	resp := HealthResponse{
		Status:    "ok",
		Timestamp: time.Now().UTC().Format(time.RFC3339),
	}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(resp)
}

// CountWords returns the number of words in the given text.
func CountWords(text string) int {
	return len(strings.Fields(text))
}

// IsPalindrome checks if a string is a palindrome (ignoring case and non-alpha chars).
func IsPalindrome(s string) bool {
	cleaned := make([]rune, 0, len(s))
	for _, r := range strings.ToLower(s) {
		if unicode.IsLetter(r) || unicode.IsDigit(r) {
			cleaned = append(cleaned, r)
		}
	}
	for i, j := 0, len(cleaned)-1; i < j; i, j = i+1, j-1 {
		if cleaned[i] != cleaned[j] {
			return false
		}
	}
	return true
}

// CamelToSnake converts a camelCase string to snake_case.
func CamelToSnake(s string) string {
	var result strings.Builder
	for i, r := range s {
		if unicode.IsUpper(r) {
			if i > 0 {
				result.WriteRune('_')
			}
			result.WriteRune(unicode.ToLower(r))
		} else {
			result.WriteRune(r)
		}
	}
	return result.String()
}

// FormatBytes converts bytes to a human-readable string (KB, MB, GB).
func FormatBytes(bytes int64) string {
	const (
		KB int64 = 1024
		MB int64 = KB * 1024
		GB int64 = MB * 1024
	)
	switch {
	case bytes >= GB:
		return fmt.Sprintf("%.1f GB", float64(bytes)/float64(GB))
	case bytes >= MB:
		return fmt.Sprintf("%.1f MB", float64(bytes)/float64(MB))
	case bytes >= KB:
		return fmt.Sprintf("%.1f KB", float64(bytes)/float64(KB))
	default:
		return fmt.Sprintf("%d B", bytes)
	}
}
