"""Append-only changelog history (Phase C2).

The plain `<deck>.changelog.json` only carries the *latest* round's diff —
which means round 3 cannot see what the user touched in round 1. AI then
risks stomping early edits.

This module persists every round into `<deck>.changelog.history.jsonl`
(one JSON object per line), and exposes the union of user-touched
`data-oid` values across the entire history. That union is the
authoritative "do not stomp" list AI consumes on the next refinement turn.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


_OID_RE = re.compile(r'data-oid="([^"]+)"')


def history_path_for(html_path: str) -> Path:
    """Return the path to `<deck>.changelog.history.jsonl` for the given deck."""
    p = Path(html_path)
    return p.parent / f"{p.stem}.changelog.history.jsonl"


def append_changelog_history(html_path: str, changelog: dict) -> None:
    """Append one changelog round as a single JSONL line."""
    path = history_path_for(html_path)
    line = json.dumps(changelog, ensure_ascii=False)
    with path.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_history(html_path: str) -> list[dict]:
    """Return all recorded changelog rounds, oldest first."""
    path = history_path_for(html_path)
    if not path.exists():
        return []
    rounds: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rounds.append(json.loads(line))
        except json.JSONDecodeError:
            # Tolerate corrupt lines rather than failing the whole load.
            continue
    return rounds


def touched_oids(html_path: str) -> set[str]:
    """Return the union of all `data-oid` values touched across history."""
    oids: set[str] = set()
    for round_data in load_history(html_path):
        for change in round_data.get("changes", []):
            sel = change.get("selector", "")
            m = _OID_RE.search(sel)
            if m:
                oids.add(m.group(1))
    return oids
