# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

"""Plugin discovery and loading.

Finds workflow.py files in the plugins/ directory and loads them.
Each plugin must define a subclass of Workflow.
"""
import importlib.util
from pathlib import Path
from pipewright.workflow import Workflow


def discover_plugins(plugins_dir: Path) -> dict[str, Workflow]:
    """Scan plugins_dir for workflow definitions.

    Returns dict mapping workflow name -> Workflow instance.
    """
    workflows = {}

    if not plugins_dir.exists():
        return workflows

    for plugin_dir in plugins_dir.iterdir():
        if not plugin_dir.is_dir():
            continue
        workflow_file = plugin_dir / "workflow.py"
        if not workflow_file.exists():
            continue

        # Dynamically import the workflow module
        spec = importlib.util.spec_from_file_location(
            f"plugins.{plugin_dir.name}.workflow", workflow_file
        )
        if spec is None or spec.loader is None:
            continue

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Find all Workflow subclasses in the module
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (
                isinstance(attr, type)
                and issubclass(attr, Workflow)
                and attr is not Workflow
                and attr.name  # must have a name defined
            ):
                workflows[attr.name] = attr()

    return workflows
