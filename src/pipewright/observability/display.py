# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

"""Terminal display formatting for real-time observability."""
from datetime import datetime
from pipewright import __version__

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
MAGENTA = "\033[35m"
BLUE = "\033[34m"


def _ts():
    return datetime.now().strftime("%H:%M:%S")


def step_banner(step_name: str, step_num: int, total: int):
    line = "=" * 50
    print(f"\n{BOLD}{CYAN}{line}{RESET}")
    print(f"{BOLD}{CYAN}  [{step_num}/{total}] {step_name}{RESET}")
    print(f"{BOLD}{CYAN}{line}{RESET}\n")


def agent_start(agent_name: str):
    print(f"  {MAGENTA}{_ts()} [AGENT]{RESET} {BOLD}{agent_name}{RESET} activated")


def agent_done(agent_name: str):
    print(f"  {MAGENTA}{_ts()} [AGENT]{RESET} {agent_name} complete")


def tool_call(tool_name: str, summary: str = ""):
    print(f"    {DIM}{_ts()} [TOOL]{RESET} {YELLOW}{tool_name}{RESET} {DIM}{summary}{RESET}")


def tool_result(tool_name: str):
    print(f"    {DIM}{_ts()} [DONE]{RESET} {tool_name}")


def info(message: str):
    print(f"  {BLUE}{_ts()} [INFO]{RESET} {message}")


def success(message: str):
    print(f"  {GREEN}{_ts()} [ OK ]{RESET} {message}")


def error(message: str):
    print(f"  {RED}{_ts()} [ERR ]{RESET} {message}")


def checkpoint_prompt(message: str) -> str:
    """Pause at a checkpoint and ask user to continue."""
    print(f"\n{BOLD}{GREEN}  >> {message}{RESET}")
    try:
        return input(f"  {DIM}Continue? [y/n/feedback]: {RESET}").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return "n"


def workflow_start(workflow_name: str, description: str):
    """Display workflow start banner with version and workflow info."""
    # Build the header box
    title = f"PIPEWRIGHT v{__version__}"
    workflow_line = f"Workflow: {workflow_name}"

    # Calculate box width (minimum 40, max of title or workflow line + padding)
    width = max(40, len(title) + 4, len(workflow_line) + 4)

    # Create padded lines
    title_padded = title.center(width - 2)
    workflow_padded = workflow_line.ljust(width - 2)

    # Draw box
    top = "╭" + "─" * width + "╮"
    bottom = "╰" + "─" * width + "╯"

    print(f"\n{BOLD}{CYAN}{top}{RESET}")
    print(f"{BOLD}{CYAN}│ {title_padded} │{RESET}")
    print(f"{BOLD}{CYAN}│ {workflow_padded} │{RESET}")
    print(f"{BOLD}{CYAN}{bottom}{RESET}\n")


def welcome():
    print(f"""
{BOLD}{CYAN}
  ╔══════════════════════════════════════════════╗
  ║          Pipewright v0.1.0                   ║
  ║   The playwright of dev pipelines            ║
  ╚══════════════════════════════════════════════╝
{RESET}""")


def result_box(title: str, content: str):
    """Display results in a bordered box."""
    lines = content.strip().split("\n")
    max_len = max((len(line) for line in lines), default=40)
    border = "─" * (max_len + 4)
    print(f"\n  {BOLD}┌─ {title} {border[len(title)+3:]}{RESET}")
    for line in lines:
        print(f"  {DIM}│{RESET}  {line}")
    print(f"  {BOLD}└{border}─┘{RESET}\n")
