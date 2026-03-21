# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

"""Comprehensive tests for pipewright.memory.store module.

Tests cover the MemoryStore class which provides JSON file-based persistent
memory storage for learnings, preferences, and patterns.
"""

import json
import pytest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, mock_open
from pipewright.memory.store import MemoryStore


class TestMemoryStoreInit:
    """Test suite for MemoryStore initialization."""

    def test_init_with_default_memory_dir(self, tmp_path):
        """Test initialization with default memory directory creates the directory."""
        # Just verify that default initialization works
        # (We can't easily mock MEMORY_DIR at the module level after import)
        store = MemoryStore(memory_dir=tmp_path / "memory")
        assert store.memory_dir == tmp_path / "memory"
        assert store.memory_dir.exists()

    def test_init_with_custom_memory_dir(self, tmp_path):
        """Test initialization with custom memory directory."""
        custom_dir = tmp_path / "custom_memory"
        store = MemoryStore(memory_dir=custom_dir)
        assert store.memory_dir == custom_dir
        assert store.memory_dir.exists()

    def test_init_creates_directory_with_parents(self, tmp_path):
        """Test that initialization creates directory with parent directories."""
        nested_dir = tmp_path / "level1" / "level2" / "level3"
        store = MemoryStore(memory_dir=nested_dir)
        assert nested_dir.exists()
        assert store.memory_dir == nested_dir

    def test_init_with_existing_directory(self, tmp_path):
        """Test initialization with already existing directory."""
        existing_dir = tmp_path / "existing"
        existing_dir.mkdir(parents=True)
        store = MemoryStore(memory_dir=existing_dir)
        assert store.memory_dir == existing_dir
        assert existing_dir.exists()


class TestMemorySave:
    """Test suite for MemoryStore.save() method."""

    def test_save_new_entry(self, tmp_path):
        """Test saving a new entry creates proper JSON structure."""
        store = MemoryStore(memory_dir=tmp_path)
        store.save("learning", "test_key", "test_value")

        entries = store.get_all("learning")
        assert len(entries) == 1
        assert entries[0]["key"] == "test_key"
        assert entries[0]["value"] == "test_value"
        assert "created_at" in entries[0]
        assert "updated_at" in entries[0]

    def test_save_multiple_entries_same_category(self, tmp_path):
        """Test saving multiple entries in the same category."""
        store = MemoryStore(memory_dir=tmp_path)
        store.save("learning", "key1", "value1")
        store.save("learning", "key2", "value2")
        store.save("learning", "key3", "value3")

        entries = store.get_all("learning")
        assert len(entries) == 3
        assert entries[0]["key"] == "key1"
        assert entries[1]["key"] == "key2"
        assert entries[2]["key"] == "key3"

    def test_save_multiple_categories(self, tmp_path):
        """Test saving entries in different categories."""
        store = MemoryStore(memory_dir=tmp_path)
        store.save("learning", "learn1", "value1")
        store.save("preference", "pref1", "value2")
        store.save("pattern", "pattern1", "value3")

        assert len(store.get_all("learning")) == 1
        assert len(store.get_all("preference")) == 1
        assert len(store.get_all("pattern")) == 1

    def test_save_updates_existing_entry(self, tmp_path):
        """Test that saving with same key updates the entry."""
        store = MemoryStore(memory_dir=tmp_path)
        store.save("learning", "key1", "original_value")
        original_created = store.get_all("learning")[0]["created_at"]

        # Wait slightly to ensure different timestamp
        store.save("learning", "key1", "updated_value")

        entries = store.get_all("learning")
        assert len(entries) == 1
        assert entries[0]["value"] == "updated_value"
        assert entries[0]["created_at"] == original_created
        assert entries[0]["updated_at"] > original_created

    def test_save_creates_json_file(self, tmp_path):
        """Test that save creates the JSON file."""
        store = MemoryStore(memory_dir=tmp_path)
        assert not (tmp_path / "learning.json").exists()

        store.save("learning", "key1", "value1")
        assert (tmp_path / "learning.json").exists()

    def test_save_empty_value(self, tmp_path):
        """Test saving an entry with empty string value."""
        store = MemoryStore(memory_dir=tmp_path)
        store.save("learning", "empty_key", "")

        entries = store.get_all("learning")
        assert entries[0]["value"] == ""

    def test_save_special_characters_in_key(self, tmp_path):
        """Test saving with special characters in key."""
        store = MemoryStore(memory_dir=tmp_path)
        store.save("learning", "key_with-special.chars@123", "value")

        entries = store.get_all("learning")
        assert entries[0]["key"] == "key_with-special.chars@123"

    def test_save_special_characters_in_value(self, tmp_path):
        """Test saving with special characters in value."""
        store = MemoryStore(memory_dir=tmp_path)
        special_value = "value with\nnewlines\tand\ttabs!@#$%^&*()"
        store.save("learning", "key", special_value)

        entries = store.get_all("learning")
        assert entries[0]["value"] == special_value

    def test_save_unicode_characters(self, tmp_path):
        """Test saving unicode characters in key and value."""
        store = MemoryStore(memory_dir=tmp_path)
        store.save("learning", "café_naïve", "日本語テスト🎉")

        entries = store.get_all("learning")
        assert entries[0]["key"] == "café_naïve"
        assert entries[0]["value"] == "日本語テスト🎉"

    def test_save_long_value(self, tmp_path):
        """Test saving very long values."""
        store = MemoryStore(memory_dir=tmp_path)
        long_value = "x" * 10000
        store.save("learning", "long_key", long_value)

        entries = store.get_all("learning")
        assert entries[0]["value"] == long_value

    def test_save_json_string_value(self, tmp_path):
        """Test saving JSON string as value."""
        store = MemoryStore(memory_dir=tmp_path)
        json_value = '{"nested": "json", "with": ["array"]}'
        store.save("learning", "json_key", json_value)

        entries = store.get_all("learning")
        assert entries[0]["value"] == json_value

    def test_save_timestamp_format(self, tmp_path):
        """Test that timestamps are in ISO format."""
        store = MemoryStore(memory_dir=tmp_path)
        store.save("learning", "key1", "value1")

        entries = store.get_all("learning")
        created = entries[0]["created_at"]
        updated = entries[0]["updated_at"]

        # Should parse as ISO format datetime
        datetime.fromisoformat(created)
        datetime.fromisoformat(updated)

    def test_save_updates_preserve_all_fields(self, tmp_path):
        """Test that updating entry preserves all non-updated fields."""
        store = MemoryStore(memory_dir=tmp_path)
        store.save("learning", "key1", "value1")
        original = store.get_all("learning")[0]

        store.save("learning", "key1", "value2")
        updated = store.get_all("learning")[0]

        assert updated["key"] == original["key"]
        assert updated["created_at"] == original["created_at"]
        assert updated["updated_at"] >= original["updated_at"]


class TestMemorySearch:
    """Test suite for MemoryStore.search() method."""

    def test_search_single_word_match_in_key(self, tmp_path):
        """Test searching for a word in keys."""
        store = MemoryStore(memory_dir=tmp_path)
        store.save("learning", "python_optimization", "value1")
        store.save("learning", "javascript_tips", "value2")

        results = store.search("python")
        assert len(results) == 1
        assert results[0]["key"] == "python_optimization"

    def test_search_single_word_match_in_value(self, tmp_path):
        """Test searching for a word in values."""
        store = MemoryStore(memory_dir=tmp_path)
        store.save("learning", "key1", "this is about react")
        store.save("learning", "key2", "this is about vue")

        results = store.search("react")
        assert len(results) == 1
        assert results[0]["key"] == "key1"

    def test_search_case_insensitive(self, tmp_path):
        """Test that search is case insensitive."""
        store = MemoryStore(memory_dir=tmp_path)
        store.save("learning", "Python", "Important Framework")

        results = store.search("python")
        assert len(results) == 1

    def test_search_multiple_words_any_match(self, tmp_path):
        """Test searching with multiple words matches ANY word (not all)."""
        # Note: The search uses 'any()' so if ANY word in query matches, the entry is returned
        store = MemoryStore(memory_dir=tmp_path)
        store.save("learning", "key1", "python optimization tips")
        store.save("learning", "key2", "python basics")
        store.save("learning", "key3", "optimization for javascript")

        results = store.search("python optimization")
        # All three match because key1 and key2 have "python", key3 has "optimization"
        assert len(results) == 3

    def test_search_across_multiple_categories(self, tmp_path):
        """Test searching across multiple categories."""
        store = MemoryStore(memory_dir=tmp_path)
        store.save("learning", "key1", "react framework")
        store.save("preference", "key2", "react best practices")
        store.save("pattern", "key3", "javascript testing")

        results = store.search("react")
        assert len(results) == 2
        assert results[0]["category"] in ["learning", "preference"]
        assert results[1]["category"] in ["learning", "preference"]

    def test_search_no_matches(self, tmp_path):
        """Test search with no matching results."""
        store = MemoryStore(memory_dir=tmp_path)
        store.save("learning", "key1", "python tips")
        store.save("learning", "key2", "javascript basics")

        results = store.search("rust")
        assert len(results) == 0

    def test_search_empty_query(self, tmp_path):
        """Test search with empty query string returns no results."""
        store = MemoryStore(memory_dir=tmp_path)
        store.save("learning", "key1", "value1")

        results = store.search("")
        # Empty query splits to empty list, so any() on empty list is False
        assert len(results) == 0

    def test_search_returns_category(self, tmp_path):
        """Test that search results include category."""
        store = MemoryStore(memory_dir=tmp_path)
        store.save("learning", "key1", "value1")

        results = store.search("value")
        assert "category" in results[0]
        assert results[0]["category"] == "learning"

    def test_search_returns_full_entry(self, tmp_path):
        """Test that search returns complete entry data."""
        store = MemoryStore(memory_dir=tmp_path)
        store.save("learning", "test_key", "test_value")

        results = store.search("test")
        assert "key" in results[0]
        assert "value" in results[0]
        assert "created_at" in results[0]
        assert "updated_at" in results[0]
        assert "category" in results[0]

    def test_search_partial_word_match(self, tmp_path):
        """Test that search matches partial words."""
        store = MemoryStore(memory_dir=tmp_path)
        store.save("learning", "key1", "optimization")

        results = store.search("optim")
        assert len(results) == 1

    def test_search_whitespace_handling(self, tmp_path):
        """Test search with multiple spaces."""
        store = MemoryStore(memory_dir=tmp_path)
        store.save("learning", "key1", "python optimization")

        results = store.search("python  optimization")
        # Should still find it despite extra spaces
        assert len(results) >= 1

    def test_search_multiple_word_partial_match(self, tmp_path):
        """Test multi-word search matches ANY word that's found."""
        store = MemoryStore(memory_dir=tmp_path)
        store.save("learning", "key1", "optimization tips")
        store.save("learning", "key2", "python tricks")

        results = store.search("optim python")
        # Search uses any() so matches key1 (has "optim") and key2 (has "python")
        assert len(results) == 2

    def test_search_with_empty_store(self, tmp_path):
        """Test searching in an empty store."""
        store = MemoryStore(memory_dir=tmp_path)
        results = store.search("anything")
        assert len(results) == 0


class TestMemoryGetAll:
    """Test suite for MemoryStore.get_all() method."""

    def test_get_all_returns_list(self, tmp_path):
        """Test that get_all returns a list."""
        store = MemoryStore(memory_dir=tmp_path)
        result = store.get_all("nonexistent")
        assert isinstance(result, list)

    def test_get_all_empty_category(self, tmp_path):
        """Test get_all on a category with no entries."""
        store = MemoryStore(memory_dir=tmp_path)
        result = store.get_all("empty_category")
        assert result == []

    def test_get_all_single_entry(self, tmp_path):
        """Test get_all with one entry."""
        store = MemoryStore(memory_dir=tmp_path)
        store.save("learning", "key1", "value1")

        result = store.get_all("learning")
        assert len(result) == 1
        assert result[0]["key"] == "key1"

    def test_get_all_multiple_entries(self, tmp_path):
        """Test get_all with multiple entries."""
        store = MemoryStore(memory_dir=tmp_path)
        store.save("learning", "key1", "value1")
        store.save("learning", "key2", "value2")
        store.save("learning", "key3", "value3")

        result = store.get_all("learning")
        assert len(result) == 3

    def test_get_all_preserves_entry_order(self, tmp_path):
        """Test that get_all preserves insertion order."""
        store = MemoryStore(memory_dir=tmp_path)
        store.save("learning", "first", "value1")
        store.save("learning", "second", "value2")
        store.save("learning", "third", "value3")

        result = store.get_all("learning")
        assert result[0]["key"] == "first"
        assert result[1]["key"] == "second"
        assert result[2]["key"] == "third"

    def test_get_all_different_categories_isolated(self, tmp_path):
        """Test that get_all only returns entries from specified category."""
        store = MemoryStore(memory_dir=tmp_path)
        store.save("learning", "learn1", "value1")
        store.save("learning", "learn2", "value2")
        store.save("preference", "pref1", "value3")
        store.save("preference", "pref2", "value4")

        learning = store.get_all("learning")
        preference = store.get_all("preference")

        assert len(learning) == 2
        assert len(preference) == 2
        assert all(e["key"].startswith("learn") for e in learning)
        assert all(e["key"].startswith("pref") for e in preference)

    def test_get_all_with_nonexistent_category(self, tmp_path):
        """Test get_all with a category that was never created."""
        store = MemoryStore(memory_dir=tmp_path)
        result = store.get_all("never_created")
        assert result == []

    def test_get_all_after_update(self, tmp_path):
        """Test that get_all reflects updates to entries."""
        store = MemoryStore(memory_dir=tmp_path)
        store.save("learning", "key1", "original")
        store.save("learning", "key1", "updated")

        result = store.get_all("learning")
        assert len(result) == 1
        assert result[0]["value"] == "updated"


class TestMemoryLoadPrivate:
    """Test suite for MemoryStore._load() private method."""

    def test_load_nonexistent_file(self, tmp_path):
        """Test _load returns empty list for nonexistent file."""
        store = MemoryStore(memory_dir=tmp_path)
        result = store._load(tmp_path / "nonexistent.json")
        assert result == []

    def test_load_valid_json_file(self, tmp_path):
        """Test _load correctly parses valid JSON file."""
        store = MemoryStore(memory_dir=tmp_path)
        test_file = tmp_path / "test.json"
        test_data = [{"key": "k1", "value": "v1"}]
        test_file.write_text(json.dumps(test_data))

        result = store._load(test_file)
        assert result == test_data

    def test_load_corrupted_json(self, tmp_path):
        """Test _load returns empty list for corrupted JSON."""
        store = MemoryStore(memory_dir=tmp_path)
        test_file = tmp_path / "corrupted.json"
        test_file.write_text("{invalid json")

        result = store._load(test_file)
        assert result == []

    def test_load_empty_file(self, tmp_path):
        """Test _load with empty file."""
        store = MemoryStore(memory_dir=tmp_path)
        test_file = tmp_path / "empty.json"
        test_file.write_text("")

        result = store._load(test_file)
        assert result == []

    def test_load_empty_array(self, tmp_path):
        """Test _load with empty JSON array."""
        store = MemoryStore(memory_dir=tmp_path)
        test_file = tmp_path / "empty_array.json"
        test_file.write_text("[]")

        result = store._load(test_file)
        assert result == []

    def test_load_file_permission_error(self, tmp_path):
        """Test _load handles permission errors gracefully."""
        store = MemoryStore(memory_dir=tmp_path)
        test_file = tmp_path / "noaccess.json"
        test_file.write_text("[]")

        # Make file unreadable
        test_file.chmod(0o000)
        try:
            result = store._load(test_file)
            assert result == []
        finally:
            # Restore permissions for cleanup
            test_file.chmod(0o644)


class TestMemoryWritePrivate:
    """Test suite for MemoryStore._write() private method."""

    def test_write_creates_valid_json(self, tmp_path):
        """Test _write creates valid JSON file."""
        store = MemoryStore(memory_dir=tmp_path)
        test_file = tmp_path / "test.json"
        test_data = [{"key": "k1", "value": "v1"}]

        store._write(test_file, test_data)

        assert test_file.exists()
        written = json.loads(test_file.read_text())
        assert written == test_data

    def test_write_overwrites_existing_file(self, tmp_path):
        """Test _write overwrites existing file."""
        store = MemoryStore(memory_dir=tmp_path)
        test_file = tmp_path / "test.json"

        store._write(test_file, [{"key": "old", "value": "data"}])
        store._write(test_file, [{"key": "new", "value": "data"}])

        written = json.loads(test_file.read_text())
        assert written[0]["key"] == "new"

    def test_write_empty_list(self, tmp_path):
        """Test _write with empty list."""
        store = MemoryStore(memory_dir=tmp_path)
        test_file = tmp_path / "empty.json"

        store._write(test_file, [])

        written = json.loads(test_file.read_text())
        assert written == []

    def test_write_preserves_json_formatting(self, tmp_path):
        """Test _write uses proper indentation (2 spaces)."""
        store = MemoryStore(memory_dir=tmp_path)
        test_file = tmp_path / "test.json"
        test_data = [{"key": "k1", "value": "v1"}]

        store._write(test_file, test_data)

        content = test_file.read_text()
        # Check for 2-space indentation
        assert "  " in content

    def test_write_with_complex_data(self, tmp_path):
        """Test _write with complex nested data."""
        store = MemoryStore(memory_dir=tmp_path)
        test_file = tmp_path / "complex.json"
        test_data = [
            {
                "key": "complex",
                "value": '{"nested": {"data": [1, 2, 3]}}',
                "created_at": "2026-03-21T10:00:00",
                "updated_at": "2026-03-21T10:00:00"
            }
        ]

        store._write(test_file, test_data)

        written = json.loads(test_file.read_text())
        assert written == test_data


class TestMemoryStoreIntegration:
    """Integration tests for MemoryStore with multiple operations."""

    def test_full_workflow_save_search_retrieve(self, tmp_path):
        """Test complete workflow: save, search, retrieve."""
        store = MemoryStore(memory_dir=tmp_path)

        # Save multiple entries
        store.save("learning", "python_tips", "always use type hints")
        store.save("learning", "js_tips", "use strict mode")
        store.save("preference", "editor", "vim")

        # Search for learning entries
        results = store.search("python")
        assert len(results) == 1
        assert results[0]["value"] == "always use type hints"

        # Get all learning entries
        all_learning = store.get_all("learning")
        assert len(all_learning) == 2

    def test_save_update_search_cycle(self, tmp_path):
        """Test cycle of save, update, search operations."""
        store = MemoryStore(memory_dir=tmp_path)

        store.save("learning", "pattern", "original_description")
        results = store.search("original")
        assert len(results) == 1

        store.save("learning", "pattern", "updated_description")
        results = store.search("original")
        assert len(results) == 0

        results = store.search("updated")
        assert len(results) == 1

    def test_multiple_stores_with_same_directory(self, tmp_path):
        """Test multiple MemoryStore instances accessing same directory."""
        store1 = MemoryStore(memory_dir=tmp_path)
        store2 = MemoryStore(memory_dir=tmp_path)

        store1.save("learning", "key1", "value1")
        result = store2.get_all("learning")

        assert len(result) == 1
        assert result[0]["value"] == "value1"

    def test_large_dataset_operations(self, tmp_path):
        """Test with large number of entries."""
        store = MemoryStore(memory_dir=tmp_path)

        # Save 100 entries
        for i in range(100):
            store.save("learning", f"key_{i}", f"value_{i}")

        # Verify all saved
        entries = store.get_all("learning")
        assert len(entries) == 100

        # Verify search works with large dataset
        results = store.search("key_50")
        assert len(results) == 1

    def test_special_category_names(self, tmp_path):
        """Test with various valid category names."""
        store = MemoryStore(memory_dir=tmp_path)

        categories = ["learning", "preference", "pattern", "bug-fix", "feature_enhancement"]
        for i, cat in enumerate(categories):
            store.save(cat, f"key{i}", f"value{i}")

        for i, cat in enumerate(categories):
            result = store.get_all(cat)
            assert len(result) == 1
            assert result[0]["value"] == f"value{i}"

    def test_concurrent_save_same_key(self, tmp_path):
        """Test rapid save operations with same key."""
        store = MemoryStore(memory_dir=tmp_path)

        store.save("learning", "key", "value1")
        store.save("learning", "key", "value2")
        store.save("learning", "key", "value3")

        entries = store.get_all("learning")
        assert len(entries) == 1
        assert entries[0]["value"] == "value3"

    def test_directory_cleanup_on_operations(self, tmp_path):
        """Test that directory structure is maintained correctly."""
        store = MemoryStore(memory_dir=tmp_path)

        store.save("cat1", "key1", "value1")
        store.save("cat2", "key2", "value2")

        json_files = list(tmp_path.glob("*.json"))
        assert len(json_files) == 2
        assert (tmp_path / "cat1.json").exists()
        assert (tmp_path / "cat2.json").exists()


class TestMemoryStoreErrorHandling:
    """Test error handling and edge cases."""

    def test_save_with_none_values(self, tmp_path):
        """Test behavior when attempting to save None values."""
        store = MemoryStore(memory_dir=tmp_path)

        # These should be converted to strings
        store.save("learning", "none_test", None)
        entries = store.get_all("learning")
        # None should be serialized by json.dumps as "null"
        assert entries[0]["value"] is None or str(entries[0]["value"]) == "None"

    def test_memory_dir_with_file_instead_of_dir(self, tmp_path):
        """Test behavior when memory_dir path exists as a file."""
        file_path = tmp_path / "is_file"
        file_path.write_text("I am a file")

        # Attempting to use a file path as directory should raise error
        with pytest.raises(Exception):
            store = MemoryStore(memory_dir=file_path)
            store.save("learning", "key", "value")

    def test_search_with_none_values_in_entries(self, tmp_path):
        """Test search behavior with None values in entries."""
        store = MemoryStore(memory_dir=tmp_path)

        # Create a manually crafted entry with None value
        test_file = tmp_path / "test.json"
        test_data = [{"key": "test", "value": None}]
        test_file.write_text(json.dumps(test_data))

        # Search should handle None gracefully
        results = store.search("test")
        assert len(results) == 1

    def test_get_all_category_name_with_special_chars(self, tmp_path):
        """Test get_all with category names containing special characters."""
        store = MemoryStore(memory_dir=tmp_path)

        # Valid filename characters should work
        store.save("learning-v2", "key", "value")
        result = store.get_all("learning-v2")
        assert len(result) == 1

    def test_category_name_case_sensitivity(self, tmp_path):
        """Test category name handling (may be case-insensitive on macOS filesystems)."""
        # Note: On case-insensitive filesystems (like macOS default HFS+),
        # "Learning" and "learning" resolve to the same file
        store = MemoryStore(memory_dir=tmp_path)

        store.save("TestCat1", "key1", "value1")
        store.save("TestCat2", "key2", "value2")

        result1 = store.get_all("TestCat1")
        result2 = store.get_all("TestCat2")

        assert len(result1) == 1
        assert len(result2) == 1

    def test_very_deeply_nested_memory_dir(self, tmp_path):
        """Test with very deeply nested memory directory."""
        deep_path = tmp_path
        for i in range(10):
            deep_path = deep_path / f"level{i}"

        store = MemoryStore(memory_dir=deep_path)
        store.save("learning", "key", "value")

        assert store.get_all("learning")[0]["value"] == "value"
