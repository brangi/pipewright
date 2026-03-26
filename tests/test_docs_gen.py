# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

"""Tests for the docs-gen workflow plugin."""
from pathlib import Path
from pipewright.plugins.loader import discover_plugins
from pipewright.workflow import Workflow


def test_docs_gen_discovered():
    workflows = discover_plugins(Path("plugins"))
    assert "docs-gen" in workflows


def test_docs_gen_is_workflow_subclass():
    workflows = discover_plugins(Path("plugins"))
    assert isinstance(workflows["docs-gen"], Workflow)


def test_docs_gen_has_two_steps():
    workflows = discover_plugins(Path("plugins"))
    assert len(workflows["docs-gen"].steps) == 2


def test_step_names():
    workflows = discover_plugins(Path("plugins"))
    names = [s.name for s in workflows["docs-gen"].steps]
    assert names == ["analyze-structure", "generate-docs"]


def test_checkpoints():
    workflows = discover_plugins(Path("plugins"))
    checkpoints = [s.checkpoint for s in workflows["docs-gen"].steps]
    assert checkpoints == [False, True]


def test_model_assignments():
    workflows = discover_plugins(Path("plugins"))
    models = [s.model for s in workflows["docs-gen"].steps]
    assert models == ["haiku", "sonnet"]


def test_prompts_contain_template_vars():
    workflows = discover_plugins(Path("plugins"))
    for step in workflows["docs-gen"].steps:
        assert "{target}" in step.prompt, f"Step '{step.name}' missing {{target}}"
        assert "{context}" in step.prompt, f"Step '{step.name}' missing {{context}}"


def test_generate_docs_has_write_and_edit_tools():
    workflows = discover_plugins(Path("plugins"))
    gen_step = workflows["docs-gen"].steps[1]
    assert "Write" in gen_step.tools
    assert "Edit" in gen_step.tools
