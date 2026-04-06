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
@click.option("--provider", "-p", default=None,
              help="LLM provider (anthropic, openai, ollama, groq, openrouter)")
@click.option("--yes", "-y", is_flag=True, default=False, help="Auto-approve checkpoints")
@click.option("--output", "-o", default=None,
              help="Write JSON result to file (use '-' for stdout)")
@click.option("--format", "-f", "fmt", default="text", type=click.Choice(["text", "json"]),
              help="Output format: text (default) or json")
def run(workflow: str, target: str, model: str | None, provider: str | None, yes: bool,
        output: str | None, fmt: str):
    """Run a workflow on a target file or directory.

    Examples:

        pipewright run test-gen ./src/auth.py

        pipewright run test-gen ./src/auth.py -p groq -y

        pipewright run issue-solve #42

        pipewright run test-gen ./src/auth.py --format json

        pipewright run test-gen ./src/auth.py -o result.json
    """
    # Find the plugins directory (relative to where pipewright is installed)
    import pathlib
    # Check current directory first, then package location
    plugins_dir = pathlib.Path.cwd() / "plugins"
    if not plugins_dir.exists():
        plugins_dir = pathlib.Path(__file__).parent / "plugins"

    workflows = discover_plugins(plugins_dir)

    if workflow not in workflows:
        click.echo(f"Unknown workflow: '{workflow}'")
        click.echo(f"Available: {', '.join(workflows.keys()) or '(none found)'}")
        raise SystemExit(1)

    result = engine.run(workflows[workflow], target, model_override=model, plugins_dir=plugins_dir,
                        auto_approve=yes, provider_override=provider)

    # Write structured output if requested
    if result and (output or fmt == "json"):
        json_str = result.to_json()
        if output == "-":
            click.echo(json_str)
        elif output:
            pathlib.Path(output).write_text(json_str + "\n")
            click.echo(f"Result written to {output}")
        elif fmt == "json":
            click.echo(json_str)


@main.command("list")
def list_workflows():
    """List available workflows."""
    import pathlib
    plugins_dir = pathlib.Path.cwd() / "plugins"
    if not plugins_dir.exists():
        plugins_dir = pathlib.Path(__file__).parent / "plugins"

    workflows = discover_plugins(plugins_dir)
    if not workflows:
        click.echo("No workflows found. Add plugins to ./plugins/")
        return
    click.echo("Available workflows:")
    for name, wf in workflows.items():
        click.echo(f"  {name:15s} {wf.description}")


@main.command("providers")
def list_providers():
    """List available LLM providers."""
    from pipewright.providers import available_providers
    providers = available_providers()
    if not providers:
        click.echo("No providers available.")
        return
    click.echo("Available providers:")
    for p in providers:
        click.echo(f"  {p}")


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


PROVIDER_INFO = {
    "anthropic": {
        "env_var": "ANTHROPIC_API_KEY",
        "cost": "Paid",
        "url": "https://console.anthropic.com/settings/keys",
        "description": "Claude models (haiku, sonnet, opus)",
    },
    "openai": {
        "env_var": "OPENAI_API_KEY",
        "cost": "Paid",
        "url": "https://platform.openai.com/api-keys",
        "description": "GPT-4o, GPT-4o-mini",
    },
    "groq": {
        "env_var": "GROQ_API_KEY",
        "cost": "Free tier",
        "url": "https://console.groq.com/keys",
        "description": "Qwen3, Llama 3.3 — fast inference",
    },
    "openrouter": {
        "env_var": "OPENROUTER_API_KEY",
        "cost": "Free models available",
        "url": "https://openrouter.ai/keys",
        "description": "Access 100+ models, many free",
    },
    "ollama": {
        "env_var": None,
        "cost": "Free (local)",
        "url": "https://ollama.com",
        "description": "Run models locally — no API key needed",
    },
}


@main.command()
def setup():
    """Interactive setup — configure your LLM provider and API key.

    Stores the API key in ~/.pipewright/.env and sets your default provider.

    Example:

        pipewright setup
    """
    click.echo()
    click.echo("  Welcome to Pipewright Setup")
    click.echo("  ===========================")
    click.echo()
    click.echo("  Choose an LLM provider:\n")

    providers = list(PROVIDER_INFO.items())
    for i, (name, info) in enumerate(providers, 1):
        label = f"  {i}. {name:12s}  {info['cost']:24s}  {info['description']}"
        click.echo(label)

    click.echo()
    while True:
        choice = click.prompt("  Enter number (1-5)", type=int)
        if 1 <= choice <= len(providers):
            break
        click.echo("  Invalid choice. Try again.")

    provider_name, info = providers[choice - 1]

    # Ollama needs no key
    if info["env_var"] is None:
        click.echo(f"\n  {provider_name} runs locally — no API key needed.")
        click.echo("  Make sure Ollama is running: ollama serve")
    else:
        click.echo(f"\n  Get your API key at: {info['url']}")
        click.echo()
        api_key = click.prompt(f"  Paste your {info['env_var']}", hide_input=True)

        if not api_key.strip():
            click.echo("  No key entered. Setup cancelled.")
            raise SystemExit(1)

        # Write to ~/.pipewright/.env
        env_path = cfg.CONFIG_DIR / ".env"
        cfg.CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        # Read existing env file to preserve other keys
        existing = {}
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    existing[k.strip()] = v.strip()

        existing[info["env_var"]] = api_key.strip()

        lines = [f"{k}={v}" for k, v in existing.items()]
        env_path.write_text("\n".join(lines) + "\n")
        env_path.chmod(0o600)

        click.echo(f"\n  Key saved to {env_path}")

    # Set as default provider
    cfg.set_value("provider", provider_name)

    click.echo(f"  Default provider set to: {provider_name}")
    click.echo()
    click.echo("  You're all set! Try:")
    click.echo(f"    pipewright run test-gen ./src/example.py -y")
    click.echo()


CI_PROVIDERS = {k: v for k, v in PROVIDER_INFO.items() if v["env_var"] is not None}


def _generate_workflow_yaml(workflow_name: str, provider_name: str, env_var: str) -> str:
    """Generate a GitHub Actions workflow YAML string."""
    pip_extra = "" if provider_name == "anthropic" else "[openai]"
    return (
        f"name: Pipewright\n"
        f"\n"
        f"on:\n"
        f"  pull_request:\n"
        f"    branches: [main]\n"
        f"\n"
        f"jobs:\n"
        f"  pipewright:\n"
        f"    runs-on: ubuntu-latest\n"
        f"    steps:\n"
        f"      - uses: actions/checkout@v4\n"
        f"\n"
        f"      - uses: actions/setup-python@v5\n"
        f"        with:\n"
        f'          python-version: "3.11"\n'
        f"\n"
        f"      - name: Install pipewright\n"
        f"        run: pip install pipewright{pip_extra}\n"
        f"\n"
        f"      - name: Run {workflow_name}\n"
        f"        env:\n"
        f"          {env_var}: ${{{{ secrets.{env_var} }}}}\n"
        f"        run: pipewright run {workflow_name} . -p {provider_name} -y\n"
    )


@main.command("ci-setup")
def ci_setup():
    """Generate a GitHub Actions workflow for pipewright.

    Creates .github/workflows/pipewright.yml in the current directory
    and tells you which GitHub Secret to add.

    Example:

        pipewright ci-setup
    """
    import pathlib

    click.echo()
    click.echo("  Pipewright CI Setup")
    click.echo("  ===================")

    # Discover workflows
    plugins_dir = pathlib.Path.cwd() / "plugins"
    if not plugins_dir.exists():
        plugins_dir = pathlib.Path(__file__).parent / "plugins"

    workflows = discover_plugins(plugins_dir)
    if not workflows:
        click.echo("\n  No workflows found. Add plugins to ./plugins/ first.")
        raise SystemExit(1)

    # Pick workflow
    click.echo("\n  Which workflow should CI run?\n")
    wf_list = list(workflows.items())
    for i, (name, wf) in enumerate(wf_list, 1):
        click.echo(f"  {i}. {name:15s} {wf.description}")

    click.echo()
    while True:
        wf_choice = click.prompt(f"  Enter number (1-{len(wf_list)})", type=int)
        if 1 <= wf_choice <= len(wf_list):
            break
        click.echo("  Invalid choice. Try again.")

    workflow_name = wf_list[wf_choice - 1][0]

    # Pick provider (no Ollama — won't work in CI)
    click.echo("\n  Which provider?\n")
    prov_list = list(CI_PROVIDERS.items())
    for i, (name, info) in enumerate(prov_list, 1):
        click.echo(f"  {i}. {name:12s}  {info['cost']}")

    click.echo()
    while True:
        prov_choice = click.prompt(f"  Enter number (1-{len(prov_list)})", type=int)
        if 1 <= prov_choice <= len(prov_list):
            break
        click.echo("  Invalid choice. Try again.")

    provider_name, provider_info = prov_list[prov_choice - 1]
    env_var = provider_info["env_var"]

    # Generate workflow file
    workflow_dir = pathlib.Path.cwd() / ".github" / "workflows"
    workflow_dir.mkdir(parents=True, exist_ok=True)
    workflow_file = workflow_dir / "pipewright.yml"

    yaml_content = _generate_workflow_yaml(workflow_name, provider_name, env_var)
    workflow_file.write_text(yaml_content)

    click.echo(f"\n  Created: {workflow_file}")
    click.echo()
    click.echo(f"  Next step:")
    click.echo(f"    Add {env_var} to your repo secrets:")
    click.echo(f"    GitHub -> Settings -> Secrets -> Actions -> New repository secret")
    click.echo()


@main.command()
@click.argument("session_id", required=False, default=None)
@click.option("--provider", "-p", default=None, help="Override provider for resumed session")
@click.option("--yes", "-y", is_flag=True, default=False, help="Auto-approve checkpoints")
def resume(session_id: str | None, provider: str | None, yes: bool):
    """Resume an interrupted workflow session.

    Without arguments, lists recent resumable sessions.
    With a session ID, resumes that specific session.

    Examples:

        pipewright resume

        pipewright resume a1b2c3d4e5f6
    """
    import datetime
    import pathlib
    from pipewright.session import Session

    if session_id is None:
        sessions = Session.list_recent()
        if not sessions:
            click.echo("No resumable sessions found.")
            return
        click.echo("Resumable sessions:\n")
        for s in sessions:
            ts = datetime.datetime.fromtimestamp(s.updated_at).strftime("%Y-%m-%d %H:%M")
            tgt = s.target[:30] + "..." if len(s.target) > 30 else s.target
            click.echo(
                f"  {s.id}  {s.workflow_name:15s} "
                f"step {s.current_step}/{s.total_steps}  "
                f"target={tgt}  {ts}"
            )
        click.echo(f"\nResume with: pipewright resume <session-id>")
        return

    session = Session.load(session_id)
    if not session:
        click.echo(f"Session '{session_id}' not found.")
        raise SystemExit(1)

    if session.completed:
        click.echo(f"Session '{session_id}' already completed.")
        raise SystemExit(1)

    plugins_dir = pathlib.Path.cwd() / "plugins"
    if not plugins_dir.exists():
        plugins_dir = pathlib.Path(__file__).parent / "plugins"

    workflows = discover_plugins(plugins_dir)
    if session.workflow_name not in workflows:
        click.echo(f"Workflow '{session.workflow_name}' not found.")
        raise SystemExit(1)

    engine.run(
        workflows[session.workflow_name],
        session.target,
        plugins_dir=plugins_dir,
        auto_approve=yes,
        provider_override=provider or session.provider,
        resume_session_id=session.id,
    )


@main.command()
@click.argument("session_id", required=False, default=None)
@click.option("--workflow", "-w", default=None, help="Filter by workflow name")
@click.option("--status", "-s", "status_filter", default="all",
              type=click.Choice(["completed", "incomplete", "all"]),
              help="Filter by status (default: all)")
@click.option("--limit", "-l", default=20, help="Max sessions to show (default: 20)")
@click.option("--json", "as_json", is_flag=True, default=False, help="Output as JSON")
def history(session_id: str | None, workflow: str | None, status_filter: str,
            limit: int, as_json: bool):
    """View workflow session history.

    Without arguments, lists all sessions (newest first).
    With a session ID, shows detailed view.
    Use 'clear' as session_id to remove all history.

    Examples:

        pipewright history

        pipewright history a1b2c3d4e5f6

        pipewright history --workflow test-gen --status completed

        pipewright history --json

        pipewright history clear
    """
    import json as json_mod
    from dataclasses import asdict
    from pipewright.session import Session
    from pipewright.observability.display import session_list_row, session_detail

    # Handle "clear" subcommand
    if session_id == "clear":
        if not as_json:
            if not click.confirm("Delete all session history?"):
                click.echo("Cancelled.")
                return
        count = Session.clear_all()
        if as_json:
            click.echo(json_mod.dumps({"cleared": count}))
        else:
            click.echo(f"Cleared {count} session(s).")
        return

    # Detail view for specific session
    if session_id is not None:
        session = Session.load(session_id)
        if not session:
            click.echo(f"Session '{session_id}' not found.")
            raise SystemExit(1)
        if as_json:
            click.echo(json_mod.dumps(asdict(session), indent=2))
        else:
            click.echo(session_detail(session))
        return

    # List view
    sessions = Session.list_all(workflow=workflow, status=status_filter, limit=limit)
    if not sessions:
        if as_json:
            click.echo("[]")
        else:
            click.echo("No sessions found.")
        return

    if as_json:
        click.echo(json_mod.dumps([asdict(s) for s in sessions], indent=2))
        return

    click.echo(f"\nSession history ({len(sessions)} sessions):\n")
    for s in sessions:
        click.echo(session_list_row(s))
    click.echo(f"\nDetail: pipewright history <session-id>")


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
