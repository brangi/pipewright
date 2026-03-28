# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

"""Tests for provider-agnostic message types."""
from pipewright.providers.types import ProviderStepResult


def test_step_result_defaults():
    """ProviderStepResult has sensible defaults for optional fields."""
    result = ProviderStepResult(output_text="hello")
    assert result.output_text == "hello"
    assert result.total_cost_usd is None
    assert result.num_turns == 0


def test_step_result_with_all_fields():
    """ProviderStepResult accepts all fields."""
    result = ProviderStepResult(
        output_text="Generated 5 tests",
        total_cost_usd=0.0042,
        num_turns=3,
    )
    assert result.output_text == "Generated 5 tests"
    assert result.total_cost_usd == 0.0042
    assert result.num_turns == 3


def test_step_result_cost_none_for_free_providers():
    """Free providers report None for cost."""
    result = ProviderStepResult(output_text="done", total_cost_usd=None, num_turns=1)
    assert result.total_cost_usd is None
