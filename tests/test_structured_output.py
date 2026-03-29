# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

"""Tests for structured output types (StepResult, WorkflowResult)."""
import json
from pipewright.providers.types import StepResult, WorkflowResult


def test_step_result_creation():
    """StepResult stores all fields correctly."""
    sr = StepResult(
        step_name="analyze",
        step_number=1,
        model="claude-haiku-4-5-20251001",
        output_text="Found 3 functions.",
        cost_usd=0.0012,
        num_turns=2,
        duration_seconds=4.5,
        skipped=False,
    )
    assert sr.step_name == "analyze"
    assert sr.step_number == 1
    assert sr.model == "claude-haiku-4-5-20251001"
    assert sr.output_text == "Found 3 functions."
    assert sr.cost_usd == 0.0012
    assert sr.num_turns == 2
    assert sr.duration_seconds == 4.5
    assert sr.skipped is False


def test_step_result_defaults():
    """StepResult has sensible defaults for optional fields."""
    sr = StepResult(step_name="gen", step_number=2, model="gpt-4o-mini", output_text="ok")
    assert sr.cost_usd is None
    assert sr.num_turns == 0
    assert sr.duration_seconds == 0.0
    assert sr.skipped is False


def test_workflow_result_creation():
    """WorkflowResult stores all fields correctly."""
    wr = WorkflowResult(
        workflow_name="test-gen",
        target="./src/auth.py",
        provider="anthropic",
        model_alias="haiku",
    )
    assert wr.workflow_name == "test-gen"
    assert wr.target == "./src/auth.py"
    assert wr.provider == "anthropic"
    assert wr.model_alias == "haiku"
    assert wr.steps == []
    assert wr.success is True
    assert wr.total_cost_usd == 0.0
    assert wr.total_duration_seconds == 0.0


def test_workflow_result_to_dict():
    """WorkflowResult.to_dict() produces a plain dictionary."""
    sr = StepResult(step_name="analyze", step_number=1, model="haiku", output_text="done",
                    cost_usd=0.001, num_turns=1, duration_seconds=2.0)
    wr = WorkflowResult(
        workflow_name="test-gen", target="src/x.py", provider="anthropic",
        model_alias="haiku", steps=[sr], success=True,
        total_cost_usd=0.001, total_duration_seconds=2.0,
    )
    d = wr.to_dict()
    assert isinstance(d, dict)
    assert d["workflow_name"] == "test-gen"
    assert d["target"] == "src/x.py"
    assert d["provider"] == "anthropic"
    assert d["success"] is True
    assert len(d["steps"]) == 1
    assert d["steps"][0]["step_name"] == "analyze"
    assert d["steps"][0]["cost_usd"] == 0.001


def test_workflow_result_to_json():
    """WorkflowResult.to_json() roundtrips through JSON."""
    sr = StepResult(step_name="gen", step_number=1, model="gpt-4o-mini", output_text="tests",
                    cost_usd=0.002, num_turns=3, duration_seconds=5.0)
    wr = WorkflowResult(
        workflow_name="test-gen", target="app.py", provider="openai",
        model_alias="haiku", steps=[sr], success=True,
        total_cost_usd=0.002, total_duration_seconds=5.0,
    )
    json_str = wr.to_json()
    parsed = json.loads(json_str)
    assert parsed["workflow_name"] == "test-gen"
    assert parsed["provider"] == "openai"
    assert parsed["steps"][0]["output_text"] == "tests"
    assert parsed["total_cost_usd"] == 0.002


def test_workflow_result_cost_aggregation():
    """Total cost should correctly reflect the sum of step costs."""
    steps = [
        StepResult(step_name="a", step_number=1, model="m", output_text="", cost_usd=0.01),
        StepResult(step_name="b", step_number=2, model="m", output_text="", cost_usd=0.02),
        StepResult(step_name="c", step_number=3, model="m", output_text="", cost_usd=None),
    ]
    total = sum(s.cost_usd for s in steps if s.cost_usd)
    wr = WorkflowResult(
        workflow_name="wf", target="t", provider="p", model_alias="m",
        steps=steps, total_cost_usd=total, total_duration_seconds=10.0,
    )
    assert wr.total_cost_usd == 0.03
    d = wr.to_dict()
    assert d["total_cost_usd"] == 0.03


def test_workflow_result_duration():
    """Duration is set correctly on the workflow result."""
    wr = WorkflowResult(
        workflow_name="wf", target="t", provider="p", model_alias="m",
        total_duration_seconds=12.34,
    )
    assert wr.total_duration_seconds == 12.34
    assert wr.to_dict()["total_duration_seconds"] == 12.34


def test_workflow_result_failed():
    """WorkflowResult can represent a failed/aborted workflow."""
    sr = StepResult(step_name="analyze", step_number=1, model="m", output_text="(aborted)",
                    skipped=True, duration_seconds=0.5)
    wr = WorkflowResult(
        workflow_name="wf", target="t", provider="p", model_alias="m",
        steps=[sr], success=False, total_duration_seconds=0.5,
    )
    assert wr.success is False
    d = wr.to_dict()
    assert d["success"] is False
    assert d["steps"][0]["skipped"] is True
