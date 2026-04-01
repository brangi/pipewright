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


class TestPermissionEdgeCases:

    def test_unknown_tool_infers_full(self):
        """Unknown tools (not in any level) should infer 'full'."""
        assert _infer_permission(["CustomTool"]) == "full"

    def test_mixed_known_and_unknown_tools(self):
        """A step with Read + unknown tool gets 'full'."""
        assert _infer_permission(["Read", "MySpecialTool"]) == "full"

    def test_write_cap_blocks_bash_step(self):
        """max_permission=write should block a step needing Bash."""
        step = Step(name="test", prompt="", tools=["Read", "Bash"])
        err = _validate_permissions(step, max_permission="write")
        assert err is not None
        assert "full" in err

    def test_read_cap_blocks_write_step(self):
        """max_permission=read should block a step needing Write."""
        step = Step(name="test", prompt="", tools=["Read", "Write"])
        err = _validate_permissions(step, max_permission="read")
        assert err is not None

    def test_explicit_full_permission_with_read_tools(self):
        """A step can declare full permission even with read-only tools."""
        step = Step(name="test", prompt="", tools=["Read"], permission_level="full")
        assert _validate_permissions(step, None) is None

    def test_step_permission_level_field_defaults_to_none(self):
        step = Step(name="test", prompt="")
        assert step.permission_level is None

    def test_step_permission_level_can_be_set(self):
        step = Step(name="test", prompt="", permission_level="write")
        assert step.permission_level == "write"

    def test_each_plugin_step_tools_exist_in_permission_table(self):
        """Every tool used in plugins should be in the permission table."""
        all_known = PERMISSION_TOOLS["full"]
        workflows = discover_plugins(Path("plugins"))
        for wf_name, wf in workflows.items():
            for step in wf.steps:
                for tool in step.tools:
                    assert tool in all_known, (
                        f"{wf_name}/{step.name} uses unknown tool '{tool}'"
                    )
