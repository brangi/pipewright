# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

"""Tests for the refactor workflow plugin."""
from pathlib import Path
from pipewright.plugins.loader import discover_plugins
from pipewright.workflow import Workflow


def test_refactor_discovered():
    workflows = discover_plugins(Path("plugins"))
    assert "refactor" in workflows


def test_refactor_is_workflow_subclass():
    workflows = discover_plugins(Path("plugins"))
    assert isinstance(workflows["refactor"], Workflow)


def test_refactor_has_four_steps():
    workflows = discover_plugins(Path("plugins"))
    assert len(workflows["refactor"].steps) == 4


def test_step_names():
    workflows = discover_plugins(Path("plugins"))
    names = [s.name for s in workflows["refactor"].steps]
    assert names == ["analyze-code", "identify-improvements", "plan-refactor", "apply-changes"]


def test_checkpoints():
    workflows = discover_plugins(Path("plugins"))
    checkpoints = [s.checkpoint for s in workflows["refactor"].steps]
    assert checkpoints == [False, False, True, True]


def test_model_assignments():
    workflows = discover_plugins(Path("plugins"))
    models = [s.model for s in workflows["refactor"].steps]
    assert models == ["haiku", "haiku", "sonnet", "sonnet"]


def test_prompts_contain_template_vars():
    workflows = discover_plugins(Path("plugins"))
    for step in workflows["refactor"].steps:
        assert "{target}" in step.prompt, f"Step '{step.name}' missing {{target}}"
        assert "{context}" in step.prompt, f"Step '{step.name}' missing {{context}}"


def test_apply_changes_has_write_and_edit_tools():
    workflows = discover_plugins(Path("plugins"))
    apply_step = workflows["refactor"].steps[3]
    assert "Write" in apply_step.tools
    assert "Edit" in apply_step.tools
    assert "Bash" in apply_step.tools
