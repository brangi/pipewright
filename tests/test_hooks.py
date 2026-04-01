# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

"""Tests for workflow hooks."""

from pathlib import Path

from pipewright.plugins.loader import discover_plugins
from pipewright.workflow import HookContext, Workflow, Step


class TestHookContext:

    def test_creation_with_defaults(self):
        ctx = HookContext(workflow_name="test")
        assert ctx.workflow_name == "test"
        assert ctx.step_name is None
        assert ctx.abort is False
        assert ctx.inject_context is None

    def test_all_fields(self):
        ctx = HookContext(
            workflow_name="wf", step_name="s1", step_number=1,
            total_steps=3, output_text="out", cost_usd=0.01,
            duration_seconds=1.5, context="ctx", target="./src",
        )
        assert ctx.step_name == "s1"
        assert ctx.cost_usd == 0.01

    def test_abort_flag(self):
        ctx = HookContext(workflow_name="test")
        ctx.abort = True
        assert ctx.abort is True

    def test_inject_context(self):
        ctx = HookContext(workflow_name="test")
        ctx.inject_context = "extra info"
        assert ctx.inject_context == "extra info"


class TestWorkflowHooks:

    def test_hooks_default_to_none(self):
        wf = Workflow()
        assert wf.on_start is None
        assert wf.on_step_complete is None
        assert wf.on_complete is None

    def test_existing_plugins_have_no_hooks(self):
        workflows = discover_plugins(Path("plugins"))
        for name, wf in workflows.items():
            assert wf.on_start is None, f"{name} has on_start hook"
            assert wf.on_step_complete is None, f"{name} has on_step_complete hook"
            assert wf.on_complete is None, f"{name} has on_complete hook"

    def test_workflow_with_on_start(self):
        calls = []

        class HookedWorkflow(Workflow):
            name = "hooked"
            description = "test"
            steps = [Step(name="s1", prompt="{target}{context}")]
            on_start = staticmethod(lambda ctx: calls.append(("start", ctx.workflow_name)))

        wf = HookedWorkflow()
        ctx = HookContext(workflow_name=wf.name, target="./src")
        wf.on_start(ctx)
        assert calls == [("start", "hooked")]

    def test_workflow_with_on_step_complete(self):
        calls = []

        class HookedWorkflow(Workflow):
            name = "hooked"
            description = "test"
            steps = [Step(name="s1", prompt="{target}{context}")]
            on_step_complete = staticmethod(
                lambda ctx: calls.append(("step", ctx.step_name))
            )

        wf = HookedWorkflow()
        ctx = HookContext(workflow_name=wf.name, step_name="s1")
        wf.on_step_complete(ctx)
        assert calls == [("step", "s1")]

    def test_hook_can_abort(self):
        def aborter(ctx):
            ctx.abort = True

        class AbortWorkflow(Workflow):
            name = "abort-test"
            description = "test"
            steps = [Step(name="s1", prompt="{target}{context}")]
            on_start = staticmethod(aborter)

        wf = AbortWorkflow()
        ctx = HookContext(workflow_name=wf.name)
        wf.on_start(ctx)
        assert ctx.abort is True
