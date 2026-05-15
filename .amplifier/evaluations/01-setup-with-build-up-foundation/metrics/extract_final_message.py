#!/usr/bin/env python3
"""Extracts the final user-facing assistant message from the pulled DTU session.

Reads:
  <run_dir>/sessions/         (the directory pulled from the outer DTU)
  <run_dir>/stdout.txt        (used to identify which session is the root)

Writes:
  <run_dir>/agent-final-message.md   (the last assistant message from the root
                                      session, in plain markdown)
  <run_dir>/agent-final-message.json (structured fields for downstream tools)

The "root session" is the one whose Session ID was printed at the top of
stdout.txt — that's the session the user's prompt was given to. Its final
assistant message is the user-facing reply (the agent's hand-back).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


SESSION_ID_RE = re.compile(r"Session ID:\s*([0-9a-f-]{8,})", re.IGNORECASE)


def _find_root_session_id(stdout_path: Path) -> str | None:
    if not stdout_path.is_file():
        return None
    for line in stdout_path.read_text(errors="replace").splitlines():
        m = SESSION_ID_RE.search(line)
        if m:
            return m.group(1).strip()
    return None


def _find_transcript_for_session(sessions_root: Path, session_id: str) -> Path | None:
    candidates = list(sessions_root.rglob(f"sessions/{session_id}/transcript.jsonl"))
    if candidates:
        return candidates[0]
    candidates = list(sessions_root.rglob("transcript.jsonl"))
    for c in candidates:
        if session_id in str(c):
            return c
    return None


def _all_transcripts(sessions_root: Path) -> list[Path]:
    return sorted(sessions_root.rglob("transcript.jsonl"))


def _last_assistant_text(transcript: Path) -> str:
    """Return the concatenated `text` segments of the last assistant message."""
    last: dict | None = None
    for raw in transcript.read_text(errors="replace").splitlines():
        raw = raw.strip()
        if not raw:
            continue
        try:
            msg = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if msg.get("role") == "assistant":
            last = msg
    if last is None:
        return ""
    content = last.get("content")
    if isinstance(content, str):
        return content.strip()
    if not isinstance(content, list):
        return ""
    parts: list[str] = []
    for block in content:
        if not isinstance(block, dict):
            continue
        if block.get("type") == "text" and isinstance(block.get("text"), str):
            parts.append(block["text"])
    return "\n\n".join(p.rstrip() for p in parts).strip()


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: extract_final_message.py <run_dir>", file=sys.stderr)
        return 2

    run_dir = Path(sys.argv[1]).resolve()
    if not run_dir.is_dir():
        print(f"Not a directory: {run_dir}", file=sys.stderr)
        return 2

    sessions_root = run_dir / "sessions"
    stdout_path = run_dir / "stdout.txt"
    out_md = run_dir / "agent-final-message.md"
    out_json = run_dir / "agent-final-message.json"

    if not sessions_root.is_dir():
        out_md.write_text("_(no sessions directory pulled from outer DTU)_\n")
        out_json.write_text(json.dumps({"status": "no-sessions"}, indent=2))
        return 1

    root_session_id = _find_root_session_id(stdout_path)

    transcript_path: Path | None = None
    if root_session_id:
        transcript_path = _find_transcript_for_session(sessions_root, root_session_id)

    # Fallback: pick the transcript with the largest size (heuristic for the
    # most active / root session) if we could not identify it explicitly.
    if transcript_path is None:
        transcripts = _all_transcripts(sessions_root)
        if transcripts:
            transcript_path = max(transcripts, key=lambda p: p.stat().st_size)

    if transcript_path is None:
        out_md.write_text("_(no transcript.jsonl found in pulled sessions)_\n")
        out_json.write_text(
            json.dumps(
                {"status": "no-transcript", "root_session_id": root_session_id},
                indent=2,
            )
        )
        return 1

    final_text = _last_assistant_text(transcript_path)

    out_md.write_text(final_text + ("\n" if not final_text.endswith("\n") else ""))
    out_json.write_text(
        json.dumps(
            {
                "status": "ok" if final_text else "empty",
                "root_session_id": root_session_id,
                "transcript_path": str(transcript_path),
                "final_text_chars": len(final_text),
            },
            indent=2,
        )
    )

    # Echo to stdout too, so the runner can log a snippet.
    if final_text:
        preview = "\n".join(final_text.splitlines()[:6])
        print(preview)
        if len(final_text.splitlines()) > 6:
            print("... (truncated, full text in agent-final-message.md)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
