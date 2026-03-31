# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

"""Tests for the pipewright ci-setup command."""

from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from pipewright.cli import main, _generate_workflow_yaml, CI_PROVIDERS


class TestCiSetupCommand:
    """Tests for pipewright ci-setup."""

    def test_ci_setup_help(self):
        runner = CliRunner()
        result = runner.invoke(main, ["ci-setup", "--help"])
        assert result.exit_code == 0
        assert "GitHub Actions" in result.output

    def test_generate_workflow_yaml_groq(self):
        yaml = _generate_workflow_yaml("test-gen", "groq", "GROQ_API_KEY")
        assert "name: Pipewright" in yaml
        assert "pipewright run test-gen . -p groq -y" in yaml
        assert "GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}" in yaml
        assert "pip install pipewright[openai]" in yaml

    def test_generate_workflow_yaml_anthropic(self):
        yaml = _generate_workflow_yaml("code-review", "anthropic", "ANTHROPIC_API_KEY")
        assert "pipewright run code-review . -p anthropic -y" in yaml
        assert "ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}" in yaml
        # Anthropic doesn't need [openai] extra
        assert "pip install pipewright\n" in yaml

    def test_generate_workflow_yaml_openrouter(self):
        yaml = _generate_workflow_yaml("docs-gen", "openrouter", "OPENROUTER_API_KEY")
        assert "pipewright run docs-gen . -p openrouter -y" in yaml
        assert "pip install pipewright[openai]" in yaml

    def test_ci_setup_creates_workflow_file(self, tmp_path):
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path) as td:
            # Create a plugins dir with a mock workflow
            plugins_dir = Path(td) / "plugins" / "test_gen"
            plugins_dir.mkdir(parents=True)
            (plugins_dir / "__init__.py").write_text("")
            (plugins_dir / "workflow.py").write_text(
                "from pipewright.workflow import Workflow, Step\n"
                "class TestGenWorkflow(Workflow):\n"
                "    name = 'test-gen'\n"
                "    description = 'Generate tests'\n"
                "    steps = [Step(name='go', prompt='{target}{context}',\n"
                "             tools=['Read'], model='haiku')]\n"
            )

            # Select workflow 1, provider 2 (openai)
            result = runner.invoke(main, ["ci-setup"], input="1\n2\n")

            assert result.exit_code == 0
            assert "Created:" in result.output

            workflow_file = Path(td) / ".github" / "workflows" / "pipewright.yml"
            assert workflow_file.exists()
            content = workflow_file.read_text()
            assert "pipewright run test-gen" in content

    def test_ci_setup_shows_secret_instructions(self, tmp_path):
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path) as td:
            plugins_dir = Path(td) / "plugins" / "test_gen"
            plugins_dir.mkdir(parents=True)
            (plugins_dir / "__init__.py").write_text("")
            (plugins_dir / "workflow.py").write_text(
                "from pipewright.workflow import Workflow, Step\n"
                "class TestGenWorkflow(Workflow):\n"
                "    name = 'test-gen'\n"
                "    description = 'Generate tests'\n"
                "    steps = [Step(name='go', prompt='{target}{context}',\n"
                "             tools=['Read'], model='haiku')]\n"
            )

            # Select workflow 1, provider 1 (anthropic)
            result = runner.invoke(main, ["ci-setup"], input="1\n1\n")

            assert "ANTHROPIC_API_KEY" in result.output
            assert "Secrets" in result.output

    def test_ci_providers_excludes_ollama(self):
        """Ollama is excluded from CI providers since it needs local hardware."""
        assert "ollama" not in CI_PROVIDERS
        assert "anthropic" in CI_PROVIDERS
        assert "groq" in CI_PROVIDERS

    def test_generate_workflow_yaml_structure(self):
        """Generated YAML has valid GitHub Actions structure."""
        yaml = _generate_workflow_yaml("test-gen", "groq", "GROQ_API_KEY")
        assert yaml.startswith("name: Pipewright")
        assert "on:" in yaml
        assert "pull_request:" in yaml
        assert "jobs:" in yaml
        assert "runs-on: ubuntu-latest" in yaml
        assert "actions/checkout@v4" in yaml
        assert "actions/setup-python@v5" in yaml
        assert 'python-version: "3.11"' in yaml
