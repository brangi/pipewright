# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

"""Tests for workflow chaining: Chain dataclass, Workflow.chains, and mode resolution."""
from pathlib import Path
from pipewright.workflow import Step, Workflow, Chain
from pipewright.plugins.loader import discover_plugins


def test_chain_defaults_to_target_mode():
    """Chain mode defaults to 'target'."""
    chain = Chain(workflow="test-gen")
    assert chain.workflow == "test-gen"
    assert chain.mode == "target"


def test_chain_context_mode():
    """Chain mode can be set to 'context'."""
    chain = Chain(workflow="test-gen", mode="context")
    assert chain.mode == "context"


def test_workflow_chains_defaults_to_empty():
    """Workflow.chains defaults to empty list."""
    wf = Workflow()
    assert wf.chains == []


def test_workflow_with_chains():
    """Workflow can define chains."""

    class MyWorkflow(Workflow):
        name = "my-wf"
        description = "test"
        steps = []
        chains = [Chain("test-gen", mode="target")]

    wf = MyWorkflow()
    assert len(wf.chains) == 1
    assert wf.chains[0].workflow == "test-gen"
    assert wf.chains[0].mode == "target"


def test_existing_plugins_have_no_chains():
    """Existing plugins (test-gen, issue-solve) have empty chains by default."""
    workflows = discover_plugins(Path("plugins"))
    for name, wf in workflows.items():
        assert wf.chains == [], f"Plugin '{name}' should have no chains by default"
