# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

"""JSON file-based persistent memory store.

Stores learnings, preferences, and patterns in ~/.pipewright/memory/.
"""
import json
from pathlib import Path
from datetime import datetime
from pipewright.config import MEMORY_DIR


class MemoryStore:
    def __init__(self, memory_dir: Path = MEMORY_DIR):
        self.memory_dir = memory_dir
        self.memory_dir.mkdir(parents=True, exist_ok=True)

    def save(self, category: str, key: str, value: str):
        """Save or update a memory entry."""
        path = self.memory_dir / f"{category}.json"
        entries = self._load(path)

        # Update existing or append new
        for entry in entries:
            if entry["key"] == key:
                entry["value"] = value
                entry["updated_at"] = datetime.now().isoformat()
                self._write(path, entries)
                return

        entries.append({
            "key": key,
            "value": value,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        })
        self._write(path, entries)

    def search(self, query: str) -> list[dict]:
        """Keyword search across all memory files."""
        words = query.lower().split()
        results = []
        for path in self.memory_dir.glob("*.json"):
            category = path.stem
            for entry in self._load(path):
                text = f"{entry.get('key', '')} {entry.get('value', '')}".lower()
                if any(w in text for w in words):
                    results.append({"category": category, **entry})
        return results

    def get_all(self, category: str) -> list[dict]:
        return self._load(self.memory_dir / f"{category}.json")

    def _load(self, path: Path) -> list[dict]:
        if not path.exists():
            return []
        try:
            with open(path) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

    def _write(self, path: Path, data: list[dict]):
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
