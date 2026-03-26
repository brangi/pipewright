# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

"""Tests for the 'pipewright init' CLI command."""
from pathlib import Path
from click.testing import CliRunner
from pipewright.cli import main, _to_class_name


def test_init_creates_plugin_directory(tmp_path):
    """init creates the plugin directory structure."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(main, ["init", "my-plugin"])
        assert result.exit_code == 0
        assert Path("plugins/my_plugin/__init__.py").exists()
        assert Path("plugins/my_plugin/workflow.py").exists()
        assert Path("tests/test_my_plugin.py").exists()


def test_init_workflow_contains_correct_name(tmp_path):
    """Scaffolded workflow.py uses the correct plugin name."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        runner.invoke(main, ["init", "my-plugin"])
        content = Path("plugins/my_plugin/workflow.py").read_text()
        assert 'name = "my-plugin"' in content
        assert "class MyPluginWorkflow" in content


def test_init_files_have_mit_header(tmp_path):
    """All scaffolded files have MIT license header."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        runner.invoke(main, ["init", "test-wf"])
        for path in [
            Path("plugins/test_wf/__init__.py"),
            Path("plugins/test_wf/workflow.py"),
            Path("tests/test_test_wf.py"),
        ]:
            content = path.read_text()
            assert "Copyright (c) 2026 Gibran Rodriguez" in content
            assert "SPDX-License-Identifier: MIT" in content


def test_init_fails_if_plugin_exists(tmp_path):
    """init fails gracefully if plugin directory already exists."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        runner.invoke(main, ["init", "existing"])
        result = runner.invoke(main, ["init", "existing"])
        assert result.exit_code != 0
        assert "already exists" in result.output


def test_init_prints_created_files(tmp_path):
    """init prints the list of created files."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(main, ["init", "demo"])
        assert "__init__.py" in result.output
        assert "workflow.py" in result.output
        assert "test_demo.py" in result.output


def test_init_workflow_has_template_vars(tmp_path):
    """Scaffolded workflow steps contain {target} and {context}."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        runner.invoke(main, ["init", "new-wf"])
        content = Path("plugins/new_wf/workflow.py").read_text()
        assert "{target}" in content
        assert "{context}" in content


def test_to_class_name():
    """_to_class_name converts snake_case to PascalCase."""
    assert _to_class_name("my_plugin") == "MyPlugin"
    assert _to_class_name("test") == "Test"
    assert _to_class_name("code_review") == "CodeReview"
