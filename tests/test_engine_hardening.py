# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

"""Tests for engine hardening: Step fields, defaults, and backward compatibility."""
from pipewright.workflow import Step


def test_step_max_turns_defaults_to_none():
    """New max_turns field defaults to None."""
    step = Step(name="test", prompt="test")
    assert step.max_turns is None


def test_step_max_turns_can_be_set():
    """max_turns can be set to an integer."""
    step = Step(name="test", prompt="test", max_turns=30)
    assert step.max_turns == 30


def test_step_context_limit_defaults_to_none():
    """New context_limit field defaults to None."""
    step = Step(name="test", prompt="test")
    assert step.context_limit is None


def test_step_context_limit_can_be_set():
    """context_limit can be set to an integer."""
    step = Step(name="test", prompt="test", context_limit=5000)
    assert step.context_limit == 5000


def test_existing_step_creation_unchanged():
    """Creating a Step without new fields works identically to before."""
    step = Step(
        name="analyze",
        prompt="Analyze {target}",
        tools=["Read", "Glob"],
        checkpoint=True,
        model="haiku",
    )
    assert step.name == "analyze"
    assert step.tools == ["Read", "Glob"]
    assert step.checkpoint is True
    assert step.model == "haiku"
    assert step.max_turns is None
    assert step.context_limit is None
