# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

"""docs-gen: Generate documentation for code.

Usage: pipewright run docs-gen ./src/auth.py
       pipewright run docs-gen ./src/
"""
from pipewright.workflow import Workflow, Step


class DocsGenWorkflow(Workflow):
    name = "docs-gen"
    description = "Generate documentation: docstrings, module docs, and README sections"

    steps = [
        Step(
            name="analyze-structure",
            prompt=(
                "Analyze the code structure at {target} to prepare for documentation generation. "
                "Identify:\n"
                "- All public functions, classes, and methods (with signatures)\n"
                "- Module-level purpose and responsibilities\n"
                "- Existing documentation (docstrings, comments, README references)\n"
                "- Dependencies and how the code fits into the larger project\n"
                "- Which items are missing documentation\n"
                "Search memory for any documentation style preferences first.\n\n"
                "Context from prior steps:\n{context}"
            ),
            tools=["Read", "Glob", "Grep"],
            checkpoint=False,
            model="haiku",
        ),
        Step(
            name="generate-docs",
            prompt=(
                "Generate comprehensive documentation for {target} based on the analysis. "
                "Produce:\n"
                "1. DOCSTRINGS: Add or improve docstrings for all public functions, classes, "
                "and methods. Use the style consistent with the project. "
                "Include Args, Returns, Raises sections.\n"
                "2. MODULE DOCS: Add or improve the module-level docstring explaining purpose, "
                "usage examples, and key patterns.\n"
                "3. README SECTION: Output a markdown section describing this module.\n\n"
                "Rules:\n"
                "- Match existing documentation style in the project\n"
                "- Do not change any code logic -- only add/update documentation\n"
                "- Keep docstrings concise but complete\n"
                "Save any documentation patterns to memory.\n\n"
                "Context from prior steps:\n{context}"
            ),
            tools=["Read", "Write", "Edit", "Glob", "Grep"],
            checkpoint=True,
            model="sonnet",
        ),
    ]
