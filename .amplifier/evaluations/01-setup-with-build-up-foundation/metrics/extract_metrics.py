#!/usr/bin/env python3
"""Renders a per-run markdown summary (verdict.md) for evaluation 01.

Reads:
  <run_dir>/meta.json
  <run_dir>/metrics.json
  <run_dir>/criteria.txt
  <run_dir>/agent-final-message.md   (produced by extract_final_message.py)
  <run_dir>/stderr.txt               (used for diagnostic snippets on FAIL)

Writes the rendered markdown to stdout.

Usage:
  python3 metrics/extract_metrics.py <run_dir>
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")


def _load_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text())
    except Exception as exc:
        return {"_error": f"failed to parse {path.name}: {exc}"}


def _read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    try:
        return path.read_text(errors="replace")
    except Exception:
        return ""


def _strip_ansi(s: str) -> str:
    return ANSI_RE.sub("", s)


def _truncate(s: str, limit: int = 4000) -> str:
    if len(s) <= limit:
        return s
    return s[:limit] + f"\n\n... [truncated, {len(s) - limit} more chars]"


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: extract_metrics.py <run_dir>", file=sys.stderr)
        return 2

    run_dir = Path(sys.argv[1]).resolve()
    if not run_dir.is_dir():
        print(f"Not a directory: {run_dir}", file=sys.stderr)
        return 2

    meta = _load_json(run_dir / "meta.json")
    metrics = _load_json(run_dir / "metrics.json")
    criteria_txt = _read_text(run_dir / "criteria.txt")
    agent_final = _read_text(run_dir / "agent-final-message.md").strip()
    stderr_txt = _read_text(run_dir / "stderr.txt")

    verdict = meta.get("verdict", "UNKNOWN")
    banner = "PASS" if verdict == "PASS" else "FAIL" if verdict == "FAIL" else "UNKNOWN"

    lines: list[str] = []
    lines.append(f"# Evaluation 01: setup-with-build-up-foundation — {banner}")
    lines.append("")
    lines.append(f"- **Date / run**: {meta.get('date', '?')} / run-{meta.get('run', '?')}")
    lines.append(f"- **Wall time**: {meta.get('wall_seconds', '?')} s")
    lines.append(f"- **Outer DTU id**: `{meta.get('outer_dtu_id', '?')}`")
    inner_id_display = meta.get("inner_dtu_id") or (
        metrics.get("inner_id") if isinstance(metrics, dict) else None
    ) or "<none>"
    lines.append(f"- **Inner DTU id**: `{inner_id_display}`")
    lines.append(f"- **Amplifier exit code**: {meta.get('amplifier_exit', '?')}")
    if meta.get("notes"):
        lines.append(f"- **Notes**: {meta['notes']}")
    lines.append("")

    # ----- Agent's final message -----
    # The high-signal artifact: the user-facing reply from the amplifier
    # session running inside the outer DTU, summarizing what was accomplished
    # and giving interactive entry commands.
    lines.append("## Agent's final message (what was accomplished)")
    lines.append("")
    if agent_final:
        lines.append(_truncate(_strip_ansi(agent_final), 12000))
    else:
        lines.append("_(no agent-final-message.md found — session pull may have failed)_")
    lines.append("")

    # ----- Scenario -----
    lines.append("## Scenario (verbatim prompt to the agent)")
    lines.append("")
    prompt = (meta.get("scenario_prompt") or "").strip()
    if prompt:
        lines.append("> " + prompt.replace("\n", "\n> "))
    else:
        lines.append("_(not recorded)_")
    lines.append("")

    # ----- Criteria -----
    lines.append("## Criteria")
    lines.append("")
    if criteria_txt:
        lines.append("```")
        lines.append(criteria_txt.rstrip())
        lines.append("```")
    else:
        lines.append("_(criteria.txt missing)_")
    lines.append("")

    # ----- Structured metrics (compact) -----
    if metrics:
        lines.append("## Structured Metrics")
        lines.append("")
        for key in [
            "profile_generated",
            "profile_path",
            "inner_id",
            "inner_status",
            "inner_dtu_running",
            "amplifier_version_ok",
            "build_up_foundation_present",
            "smoke_ok",
            "handback_parts_found",
            "handback_complete",
            "handback_instance_id",
            "handback_exec",
            "handback_destroy",
            "handback_profile",
        ]:
            if key not in metrics:
                continue
            val = metrics[key]
            if isinstance(val, str) and len(val) > 100:
                val = val[:100] + "…"
            lines.append(f"- `{key}` = `{val}`")
        lines.append("")

    # ----- Inner DTU smoke output (proves end-to-end provider chain) -----
    smoke_output = metrics.get("smoke_output") if isinstance(metrics, dict) else None
    if smoke_output:
        last_lines = "\n".join(smoke_output.splitlines()[-30:])
        lines.append("## Inner DTU smoke run (last 30 lines)")
        lines.append("")
        lines.append("```")
        lines.append(_truncate(_strip_ansi(last_lines), 4000))
        lines.append("```")
        lines.append("")

    # ----- Diagnostic snippet on FAIL -----
    if verdict == "FAIL" and stderr_txt.strip():
        lines.append("## stderr.txt (last 40 lines)")
        lines.append("")
        lines.append("```")
        lines.append("\n".join(stderr_txt.splitlines()[-40:]))
        lines.append("```")
        lines.append("")

    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
