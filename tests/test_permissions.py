# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

"""Tests for plugin permission levels."""

from pathlib import Path

from pipewright.engine import (
    PERMISSION_TOOLS,
    _infer_permission,
    _validate_permissions,
)
from pipewright.plugins.loader import discover_plugins
from pipewright.workflow import Step


class TestInferPermission:

    def test_read_only_tools(self):
        assert _infer_permission(["Read", "Glob", "Grep"]) == "read"

    def test_single_read_tool(self):
        assert _infer_permission(["Read"]) == "read"

    def test_write_tools(self):
        assert _infer_permission(["Read", "Write"]) == "write"

    def test_edit_is_write(self):
        assert _infer_permission(["Read", "Edit", "Glob"]) == "write"

    def test_bash_is_full(self):
        assert _infer_permission(["Bash"]) == "full"

    def test_all_tools_is_full(self):
        assert _infer_permission(["Read", "Write", "Edit", "Glob", "Grep", "Bash"]) == "full"

    def test_empty_tools_is_read(self):
        assert _infer_permission([]) == "read"


class TestValidatePermissions:

    def test_matching_level_passes(self):
        step = Step(name="test", prompt="", tools=["Read", "Glob"], permission_level="read")
        assert _validate_permissions(step, None) is None

    def test_tools_exceed_declared_level(self):
        step = Step(name="test", prompt="", tools=["Read", "Write"], permission_level="read")
        err = _validate_permissions(step, None)
        assert err is not None
        assert "Write" in err

    def test_inferred_level_when_none(self):
        step = Step(name="test", prompt="", tools=["Read", "Glob"])
        assert _validate_permissions(step, None) is None

    def test_config_cap_blocks_higher_level(self):
        step = Step(name="test", prompt="", tools=["Read", "Write"])
        err = _validate_permissions(step, max_permission="read")
        assert err is not None
        assert "max_permission" in err

    def test_config_cap_allows_matching_level(self):
        step = Step(name="test", prompt="", tools=["Read", "Write"], permission_level="write")
        assert _validate_permissions(step, max_permission="write") is None

    def test_no_cap_allows_everything(self):
        step = Step(name="test", prompt="", tools=["Bash"], permission_level="full")
        assert _validate_permissions(step, max_permission=None) is None

    def test_full_cap_allows_everything(self):
        step = Step(name="test", prompt="", tools=["Bash"])
        assert _validate_permissions(step, max_permission="full") is None


class TestExistingPlugins:

    def test_all_plugins_have_valid_permissions(self):
        """Every step in every plugin should have tools consistent with its inferred level."""
        workflows = discover_plugins(Path("plugins"))
        for wf_name, wf in workflows.items():
            for step in wf.steps:
                err = _validate_permissions(step, None)
                assert err is None, f"{wf_name}/{step.name}: {err}"

    def test_permission_levels_table(self):
        """Verify the 3 permission levels are properly ordered."""
        assert PERMISSION_TOOLS["read"] < PERMISSION_TOOLS["write"]
        assert PERMISSION_TOOLS["write"] < PERMISSION_TOOLS["full"]
