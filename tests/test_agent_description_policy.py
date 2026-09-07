"""Delegate-catalog policy guard for this bundle's agent descriptions.

WHAT THIS PROTECTS, AND WHY IT IS WORTH A TEST
----------------------------------------------
An agent's `meta.description` is PAY-PER-TURN. Every session that mounts this
bundle carries every description in the `delegate` tool's schema, on every
request, whether or not the agent is ever delegated to. The agent BODY, by
contrast, is pay-per-use: it is read only when the agent is actually spawned.
So a worked example in a description is charged to every turn of every session
to serve the one turn that delegates -- which is why the standard puts
tutorials and examples in the body and keeps the description to a routing
decision.

The policy this pins is `foundation:context/shared/
description-authoring-principles.md` (V3: `<example>`/`<commentary>` rejected
entirely; V5: the char cap), the same policy
`foundation:recipes/validate-agents.yaml` v1.8.0 enforces as
AGENT_DESCRIPTION_ERROR_CHARS / EXAMPLE_BLOCK_PRESENT. Two checkers that
disagree about the cap are worse than one, so the numbers below are the
recipe's own.

WHY A SET WALK RATHER THAN TWO NAMED FILES
------------------------------------------
A per-file test can only guard what existed when it was written. This bundle
shipped two agents whose descriptions BOTH carried two `<example>` blocks and
both ran over 1,200 chars, and nothing in the repo noticed until a sweep looked
for it by hand. The walk covers `agents/*.md` as a SET, so an agent added later
is covered the day it lands -- and `test_the_sweep_is_not_vacuous` fails loudly
if the glob ever matches nothing, because a guard that silently disarms itself
on a directory rename is worse than no guard.

WHAT THIS CANNOT PROVE
----------------------
It is a shape check, not a quality check. It cannot tell whether a description
routes CORRECTLY -- only that it is trigger-first, within budget, carries both
routing clauses, and has no example markup. Fidelity against a previous
revision is a review-time judgment (see
`docs/lanes/dae2-catalog-amplifier-tester/DONE-NOTE.md`), not something a
static test can assert.

Pure-Python, filesystem-only: no network, no API key, no bundle load.
Run with `python3 -m pytest tests/ -q` from the repo root.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).parent.parent
AGENTS_DIR = REPO_ROOT / "agents"

# Both numbers are byte-identical to validate-agents.yaml v1.8.0's
# AGENT_DESCRIPTION_WARN_CHARS (the cap) and MIN_DESCRIPTION_LENGTH (the
# floor). The floor matters: without it a description could be "shortened"
# into uselessness to satisfy the ceiling and still pass.
MAX_DESCRIPTION_CHARS = 600
MIN_DESCRIPTION_CHARS = 100

# Trigger-first: the first clause must say WHEN to reach for the agent, not
# what it is. Anchored at the start, so a USE WHEN buried in paragraph three
# does not satisfy it.
#
# Both clause patterns are matched against WHITESPACE-NORMALISED text, never
# the raw scalar. `meta.description` is a YAML literal block, so where the
# author hard-wraps a line is a formatting choice with no meaning -- but a wrap
# landing inside "DO NOT USE WHEN" would otherwise fail a description that
# carries the clause perfectly well. A guard that fails on line-break position
# trains the next author to fight the wrapper instead of writing the clause.
TRIGGER_FIRST = re.compile(r"^USE WHEN\b")
NEGATIVE_CLAUSE = re.compile(r"\bDO NOT USE WHEN\b")
EXAMPLE_MARKUP = re.compile(r"</?(?:example|commentary)>", re.IGNORECASE)


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _agent_files() -> list[Path]:
    return sorted(AGENTS_DIR.glob("*.md"))


def _description(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    assert match is not None, f"{path.name}: no YAML frontmatter"
    front = yaml.safe_load(match.group(1))
    meta = front.get("meta") if isinstance(front, dict) else None
    assert isinstance(meta, dict), f"{path.name}: frontmatter has no meta: block"
    description = meta.get("description")
    assert isinstance(description, str), f"{path.name}: meta.description is not a string"
    return description


def _ids() -> list[str]:
    return [f"agents/{p.name}" for p in _agent_files()]


def test_the_sweep_is_not_vacuous() -> None:
    """A guard that matches zero files is decoration, not a gate."""
    assert _agent_files(), (
        "agents/*.md matched NOTHING. Either the directory moved or this guard "
        "has silently stopped guarding anything -- fix the glob, do not delete "
        "this test."
    )


@pytest.mark.parametrize("path", _agent_files(), ids=_ids())
def test_description_is_within_budget(path: Path) -> None:
    description = _description(path)
    length = len(description)
    assert length >= MIN_DESCRIPTION_CHARS, (
        f"{path.name}: description is {length} chars, under the "
        f"{MIN_DESCRIPTION_CHARS}-char floor -- too thin to route on."
    )
    assert length <= MAX_DESCRIPTION_CHARS, (
        f"{path.name}: description is {length} chars, over the "
        f"{MAX_DESCRIPTION_CHARS}-char cap. This text is charged to EVERY turn "
        f"of every session that mounts this bundle. Move the detail into the "
        f"agent body, which is only read when the agent is actually spawned."
    )


@pytest.mark.parametrize("path", _agent_files(), ids=_ids())
def test_description_is_trigger_first(path: Path) -> None:
    description = _norm(_description(path))
    assert TRIGGER_FIRST.match(description), (
        f"{path.name}: description does not open with USE WHEN. The first "
        f"clause must say WHEN to reach for this agent, not what it is -- that "
        f"is the only part a router reads before deciding."
    )


@pytest.mark.parametrize("path", _agent_files(), ids=_ids())
def test_description_carries_both_routing_clauses(path: Path) -> None:
    description = _norm(_description(path))
    assert NEGATIVE_CLAUSE.search(description), (
        f"{path.name}: description has no DO NOT USE WHEN clause. Naming the "
        f"neighbouring agent or bundle that SHOULD get the work is what stops "
        f"a near-miss delegation."
    )


@pytest.mark.parametrize("path", _agent_files(), ids=_ids())
def test_description_carries_no_example_markup(path: Path) -> None:
    description = _description(path)
    found = EXAMPLE_MARKUP.findall(description)
    assert not found, (
        f"{path.name}: description contains {len(found)} example/commentary "
        f"tag(s). These are rejected outright (description-authoring-"
        f"principles V3, validate-agents EXAMPLE_BLOCK_PRESENT) -- an agent "
        f"with none is in the required shape, not missing a feature. Worked "
        f"examples belong in the agent body."
    )
