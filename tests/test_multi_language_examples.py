# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

"""Verify multi-language examples exist and test-gen prompts are language-aware."""
from pathlib import Path

from plugins.test_gen.workflow import TestGenWorkflow


EXPECTED_EXAMPLES = {
    "python": ["utils.py"],
    "js": ["utils.js", "package.json"],
    "ts": ["utils.ts", "package.json", "tsconfig.json"],
    "java": ["Utils.java"],
    "rust": ["Cargo.toml", "src/lib.rs"],
    "go": ["go.mod", "utils.go"],
    "ruby": ["utils.rb"],
}


def test_all_example_directories_exist():
    """Every expected language directory must exist under example/."""
    root = Path("example")
    missing = []
    for lang in EXPECTED_EXAMPLES:
        if not (root / lang).is_dir():
            missing.append(lang)
    assert not missing, f"Missing example directories: {missing}"


def test_all_example_files_exist():
    """Every expected file must exist and be non-empty."""
    root = Path("example")
    missing = []
    for lang, files in EXPECTED_EXAMPLES.items():
        for f in files:
            path = root / lang / f
            if not path.exists():
                missing.append(str(path))
            elif path.stat().st_size == 0:
                missing.append(f"{path} (empty)")
    assert not missing, f"Missing or empty example files:\n" + "\n".join(f"  - {m}" for m in missing)


def test_test_gen_no_hardcoded_pytest_default():
    """test-gen generate step must not hardcode 'pytest by default'."""
    wf = TestGenWorkflow()
    generate_step = next(s for s in wf.steps if s.name == "generate")
    assert "or pytest by default" not in generate_step.prompt


def test_test_gen_mentions_multiple_frameworks():
    """test-gen generate step must reference frameworks for all supported languages."""
    wf = TestGenWorkflow()
    generate_step = next(s for s in wf.steps if s.name == "generate")
    for framework in ["pytest", "Jest", "Vitest", "JUnit", "cargo test", "RSpec"]:
        assert framework in generate_step.prompt, f"Missing framework: {framework}"


def test_test_gen_run_step_is_language_aware():
    """test-gen run step must reference language-specific run commands."""
    wf = TestGenWorkflow()
    run_step = next(s for s in wf.steps if s.name == "run")
    for cmd in ["pytest", "npx jest", "cargo test", "go test"]:
        assert cmd in run_step.prompt, f"Missing run command: {cmd}"
