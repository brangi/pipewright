"""test-gen: Generate meaningful test suites for source files.

Usage: pipewright run test-gen ./src/auth.py
"""
from pipewright.workflow import Workflow, Step


class TestGenWorkflow(Workflow):
    name = "test-gen"
    description = "Generate meaningful test suites for source files"

    steps = [
        Step(
            name="analyze",
            prompt=(
                "Analyze the source file at {target} and its surrounding codebase. "
                "Identify: what the code does, key functions/classes, dependencies, "
                "edge cases, and what testing framework is already used (if any). "
                "Search memory for any testing preferences first.\n\n"
                "Context from prior steps:\n{context}"
            ),
            tools=["Read", "Glob", "Grep"],
            checkpoint=False,
        ),
        Step(
            name="generate",
            prompt=(
                "Based on the analysis below, write a comprehensive test file for {target}. "
                "Use the testing framework already in the project, or pytest by default. "
                "Cover: happy paths, edge cases, error handling. "
                "Write the test file next to the source or in a tests/ directory.\n\n"
                "Context from prior steps:\n{context}"
            ),
            tools=["Read", "Write", "Glob"],
            checkpoint=True,  # User reviews generated tests before running
        ),
        Step(
            name="run",
            prompt=(
                "Run the test file that was just generated. Report which tests passed "
                "and which failed. If tests fail, explain why and suggest fixes. "
                "Save any useful patterns to memory for future test generation.\n\n"
                "Context from prior steps:\n{context}"
            ),
            tools=["Bash", "Read"],
            checkpoint=True,
        ),
    ]
