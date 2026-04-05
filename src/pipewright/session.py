# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

"""Session persistence for workflow resume.

Saves workflow state after each step to ~/.pipewright/sessions/.
Enables resuming crashed or interrupted workflows.
"""
import json
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path

from pipewright.config import CONFIG_DIR

SESSIONS_DIR = CONFIG_DIR / "sessions"
MAX_SESSIONS = 50


@dataclass
class Session:
    """Persistent snapshot of a workflow execution."""
    id: str
    workflow_name: str
    target: str
    provider: str
    model_alias: str
    context: str
    current_step: int  # 0-based index of the NEXT step to run
    total_steps: int
    step_results: list[dict] = field(default_factory=list)
    created_at: float = 0.0
    updated_at: float = 0.0
    completed: bool = False

    def save(self):
        """Persist session to disk."""
        SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
        self.updated_at = time.time()
        path = SESSIONS_DIR / f"{self.id}.json"
        with open(path, "w") as f:
            json.dump(asdict(self), f, indent=2)

    def mark_complete(self):
        """Mark session as completed and persist."""
        self.completed = True
        self.save()

    @staticmethod
    def load(session_id: str) -> "Session | None":
        """Load a session from disk."""
        path = SESSIONS_DIR / f"{session_id}.json"
        if not path.exists():
            return None
        try:
            with open(path) as f:
                data = json.load(f)
            return Session(**data)
        except (json.JSONDecodeError, TypeError, KeyError):
            return None

    @staticmethod
    def list_recent() -> list["Session"]:
        """List recent incomplete sessions, newest first."""
        if not SESSIONS_DIR.exists():
            return []
        sessions = []
        for path in sorted(SESSIONS_DIR.glob("*.json"),
                           key=lambda p: p.stat().st_mtime, reverse=True):
            s = Session.load(path.stem)
            if s and not s.completed:
                sessions.append(s)
        return sessions

    @staticmethod
    def list_all(
        workflow: str | None = None,
        status: str = "all",
        limit: int = 20,
    ) -> list["Session"]:
        """List sessions with optional filters, newest first."""
        if not SESSIONS_DIR.exists():
            return []
        sessions = []
        for path in sorted(SESSIONS_DIR.glob("*.json"),
                           key=lambda p: p.stat().st_mtime, reverse=True):
            s = Session.load(path.stem)
            if s is None:
                continue
            if workflow and s.workflow_name != workflow:
                continue
            if status == "completed" and not s.completed:
                continue
            if status == "incomplete" and s.completed:
                continue
            sessions.append(s)
            if len(sessions) >= limit:
                break
        return sessions

    @staticmethod
    def cleanup():
        """Remove old sessions, keeping only the most recent MAX_SESSIONS."""
        if not SESSIONS_DIR.exists():
            return
        files = sorted(SESSIONS_DIR.glob("*.json"),
                       key=lambda p: p.stat().st_mtime)
        while len(files) > MAX_SESSIONS:
            files[0].unlink()
            files.pop(0)

    @staticmethod
    def clear_all() -> int:
        """Remove all session files. Returns count deleted."""
        if not SESSIONS_DIR.exists():
            return 0
        count = 0
        for path in SESSIONS_DIR.glob("*.json"):
            path.unlink()
            count += 1
        return count


def create_session(workflow_name: str, target: str, provider: str,
                   model_alias: str, total_steps: int) -> Session:
    """Create a new session with a unique ID."""
    session = Session(
        id=uuid.uuid4().hex[:12],
        workflow_name=workflow_name,
        target=target,
        provider=provider,
        model_alias=model_alias,
        context=f"Target: {target}\n",
        current_step=0,
        total_steps=total_steps,
        created_at=time.time(),
        updated_at=time.time(),
    )
    session.save()
    Session.cleanup()
    return session
