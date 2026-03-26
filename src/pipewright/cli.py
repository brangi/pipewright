# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

"""Pipewright CLI — the user-facing entry point.

Uses Click to define commands. After `pip install pipewright`,
the `pipewright` command is available in the terminal.
"""
import click
from pipewright import __version__
from pipewright import config as cfg
from pipewright.memory.store import MemoryStore
from pipewright.plugins.loader import discover_plugins
from pipewright import engine


@click.group()
@click.version_option(version=__version__, prog_name="pipewright")
def main():
    """Pipewright — The playwright of dev pipelines.

    AI-powered workflow automation for developers.
    """
    pass


@main.command()
@click.argument("workflow")
@click.argument("target", required=False, default=".")
@click.option("--model", "-m", default=None, help="Override the model for this run")
@click.option("--yes", "-y", is_flag=True, default=False, help="Auto-approve checkpoints")
def run(workflow: str, target: str, model: str | None, yes: bool):
    """Run a workflow on a target file or directory.

    Examples:

        pipewright run test-gen ./src/auth.py

        pipewright run test-gen ./src/auth.py -y

        pipewright run issue-solve #42
    """
    # Find the plugins directory (relative to where pipewright is installed)
    import pathlib
    # Check current directory first, then package location
    plugins_dir = pathlib.Path.cwd() / "plugins"
    if not plugins_dir.exists():
        plugins_dir = pathlib.Path(__file__).parent.parent.parent.parent / "plugins"

    workflows = discover_plugins(plugins_dir)

    if workflow not in workflows:
        click.echo(f"Unknown workflow: '{workflow}'")
        click.echo(f"Available: {', '.join(workflows.keys()) or '(none found)'}")
        raise SystemExit(1)

    engine.run(workflows[workflow], target, model_override=model, plugins_dir=plugins_dir,
               auto_approve=yes)


@main.command("list")
def list_workflows():
    """List available workflows."""
    import pathlib
    plugins_dir = pathlib.Path.cwd() / "plugins"
    if not plugins_dir.exists():
        plugins_dir = pathlib.Path(__file__).parent.parent.parent.parent / "plugins"

    workflows = discover_plugins(plugins_dir)
    if not workflows:
        click.echo("No workflows found. Add plugins to ./plugins/")
        return
    click.echo("Available workflows:")
    for name, wf in workflows.items():
        click.echo(f"  {name:15s} {wf.description}")


@main.group()
def config():
    """Manage pipewright configuration."""
    pass


@config.command("set")
@click.argument("key")
@click.argument("value")
def config_set(key: str, value: str):
    """Set a config value.

    Examples:

        pipewright config set provider anthropic

        pipewright config set model haiku
    """
    cfg.set_value(key, value)
    click.echo(f"Set {key} = {value}")


@config.command("get")
@click.argument("key")
def config_get(key: str):
    """Get a config value."""
    val = cfg.get(key)
    click.echo(f"{key} = {val}")


@main.group()
def memory():
    """Interact with pipewright's persistent memory."""
    pass


@memory.command("search")
@click.argument("query")
def memory_search(query: str):
    """Search persistent memory for past learnings.

    Example:

        pipewright memory search "testing patterns"
    """
    store = MemoryStore()
    results = store.search(query)
    if not results:
        click.echo("No memories found.")
        return
    for r in results:
        click.echo(f"  [{r['category']}] {r['key']}: {r['value']}")


def _to_class_name(snake_name: str) -> str:
    """Convert snake_case to PascalCase. e.g. 'my_plugin' -> 'MyPlugin'."""
    return "".join(word.capitalize() for word in snake_name.split("_"))


@main.command()
@click.argument("name")
def init(name: str):
    """Scaffold a new plugin directory.

    Creates a plugin with a minimal Workflow template and basic tests.

    Example:

        pipewright init my-plugin
    """
    import pathlib

    dir_name = name.replace("-", "_")
    plugins_dir = pathlib.Path.cwd() / "plugins"
    plugin_dir = plugins_dir / dir_name

    if plugin_dir.exists():
        click.echo(f"Error: Plugin '{dir_name}' already exists at {plugin_dir}")
        raise SystemExit(1)

    plugin_dir.mkdir(parents=True, exist_ok=True)

    class_name = _to_class_name(dir_name)

    (plugin_dir / "__init__.py").write_text(
        "# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>\n"
        "# SPDX-License-Identifier: MIT\n"
    )

    (plugin_dir / "workflow.py").write_text(
        "# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>\n"
        "# SPDX-License-Identifier: MIT\n"
        "\n"
        f'"""{name}: TODO -- describe your workflow.\n'
        "\n"
        f"Usage: pipewright run {name} <target>\n"
        '"""\n'
        "from pipewright.workflow import Workflow, Step\n"
        "\n"
        "\n"
        f"class {class_name}Workflow(Workflow):\n"
        f'    name = "{name}"\n'
        f'    description = "TODO -- describe what this workflow does"\n'
        "\n"
        "    steps = [\n"
        "        Step(\n"
        '            name="analyze",\n'
        "            prompt=(\n"
        '                "Analyze the target at {target}. "\n'
        '                "Identify key aspects relevant to this workflow.\\n\\n"\n'
        '                "Context from prior steps:\\n{context}"\n'
        "            ),\n"
        '            tools=["Read", "Glob", "Grep"],\n'
        "            checkpoint=False,\n"
        '            model="haiku",\n'
        "        ),\n"
        "        Step(\n"
        '            name="execute",\n'
        "            prompt=(\n"
        '                "Based on the analysis, perform the main action for {target}.\\n\\n"\n'
        '                "Context from prior steps:\\n{context}"\n'
        "            ),\n"
        '            tools=["Read", "Write", "Glob"],\n'
        "            checkpoint=True,\n"
        '            model="sonnet",\n'
        "        ),\n"
        "    ]\n"
    )

    tests_dir = pathlib.Path.cwd() / "tests"
    tests_dir.mkdir(exist_ok=True)
    (tests_dir / f"test_{dir_name}.py").write_text(
        "# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>\n"
        "# SPDX-License-Identifier: MIT\n"
        "\n"
        f'"""Tests for the {name} workflow plugin."""\n'
        "from pathlib import Path\n"
        "from pipewright.plugins.loader import discover_plugins\n"
        "from pipewright.workflow import Workflow\n"
        "\n"
        "\n"
        f"def test_{dir_name}_discovered():\n"
        "    workflows = discover_plugins(Path(\"plugins\"))\n"
        f'    assert "{name}" in workflows\n'
        "\n"
        "\n"
        f"def test_{dir_name}_is_workflow_subclass():\n"
        "    workflows = discover_plugins(Path(\"plugins\"))\n"
        f'    assert isinstance(workflows["{name}"], Workflow)\n'
        "\n"
        "\n"
        f"def test_{dir_name}_prompts_contain_template_vars():\n"
        "    workflows = discover_plugins(Path(\"plugins\"))\n"
        f'    wf = workflows["{name}"]\n'
        "    for step in wf.steps:\n"
        "        assert \"{target}\" in step.prompt\n"
        "        assert \"{context}\" in step.prompt\n"
    )

    click.echo(f"Created plugin '{name}':")
    click.echo(f"  {plugin_dir / '__init__.py'}")
    click.echo(f"  {plugin_dir / 'workflow.py'}")
    click.echo(f"  {tests_dir / f'test_{dir_name}.py'}")
    click.echo(f"\nRun: pipewright list")


if __name__ == "__main__":
    main()
