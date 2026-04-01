# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

"""Tests for terminal display formatting."""
import pytest
from unittest.mock import patch
from pipewright.observability import display
from pipewright import __version__


def test_workflow_start_output(capsys):
    """Test workflow_start displays correct format with version."""
    display.workflow_start("test-gen", "Generate unit tests")
    captured = capsys.readouterr()

    # Check for version in output
    assert f"PIPEWRIGHT v{__version__}" in captured.out

    # Check for workflow name
    assert "Workflow: test-gen" in captured.out

    # Check for box drawing characters
    assert "╭" in captured.out
    assert "╰" in captured.out
    assert "│" in captured.out


def test_workflow_start_with_long_name(capsys):
    """Test workflow_start handles long workflow names."""
    long_name = "very-long-workflow-name-that-exceeds-normal-width"
    display.workflow_start(long_name, "Description")
    captured = capsys.readouterr()

    # Should still display without breaking
    assert long_name in captured.out
    assert f"v{__version__}" in captured.out


def test_workflow_start_uses_dynamic_version(capsys):
    """Test workflow_start uses __version__ from package, not hardcoded."""
    with patch("pipewright.observability.display.__version__", "0.2.0"):
        display.workflow_start("test", "Test workflow")
        captured = capsys.readouterr()
        assert "v0.2.0" in captured.out
        assert "v0.1.0" not in captured.out


def test_workflow_start_includes_workflow_name(capsys):
    """Test workflow_start output contains the given workflow name."""
    display.workflow_start("code-review", "Review code for issues")
    captured = capsys.readouterr()
    assert "code-review" in captured.out


def test_result_box_empty_content(capsys):
    """Test result_box handles empty string content without raising."""
    display.result_box("Empty Result", "")
    captured = capsys.readouterr()
    assert "Empty Result" in captured.out


def test_step_banner_includes_name_and_number(capsys):
    """Test step_banner output includes the step name and step number."""
    display.step_banner("analyze", 2, 5)
    captured = capsys.readouterr()
    assert "analyze" in captured.out
    assert "2" in captured.out


def test_error_contains_message(capsys):
    """Test error output contains the provided message text."""
    display.error("something went wrong")
    captured = capsys.readouterr()
    assert "something went wrong" in captured.out


def test_success_contains_message(capsys):
    """Test success output contains the provided message text."""
    display.success("all tests passed")
    captured = capsys.readouterr()
    assert "all tests passed" in captured.out
