"""Lean-head guardrail for `context/amplifier-tester-awareness.md`.

WHAT THIS PROTECTS, AND WHY IT IS WORTH A TEST
----------------------------------------------
This bundle's awareness file renders into the composed system head of every
session that loads the bundle, whether or not a single `amplifier-tester`
delegation is ever made. `model_performance-g7h3` bought 98 end-to-end
claude-opus-5 / S7-17 runs (49/arm, $428.10) against the lean head and all
three pre-registered estimators excluded zero for the first time in the
program:

    primary      (VALID only, n 11/8)  -13.57%  95% CI [-22.27%, -4.86%]
    ALL runs     (n 49/49)             -16.42%  95% CI [-23.29%,  -9.56%]
    block-paired (7 pairs)             -14.44%  95% CI [-26.83%,  -2.06%]

Co-primary quality is CITED from `model_performance-5zp`: one-sided 95% lower
bound -7.15 pp against the frozen -10 pp non-inferiority margin — CLEARS.
Neither is re-measured here; the spend authority for this change is $0 for
exactly that reason.

The head is shared with the Anthropic wire, where the saving rests on ONE cold
head write per session: the head must be byte-stable so `cache_read` returns to
exactly it at every compaction boundary. A head that silently regrows, or that
acquires a per-turn-varying byte, costs that advantage without anything
failing.

WHAT EACH ASSERTION CAN AND CANNOT PROVE
----------------------------------------
Stated plainly, because a guardrail whose limits are not written down gets read
as proving more than it does.

(a) BYTE PIN — fully proven here. `context/amplifier-tester-awareness.md` is
    byte-identical to span 2 of the measured V1 head, vendored verbatim in
    `tests/fixtures/lean-head-v1/`. This is the assertion that goes RED against
    the pre-change (stock) text.

(b) CHAR BUDGET — fully proven here, PER ARTIFACT. Never against a whole-head
    absolute: `zc6t` measured a real composed head at 320,410 chars against a
    shim figure of 48,249, so any whole-head number pinned in a single bundle
    repo would be false on arrival.

(c) FIDELITY — proven for an ENUMERATED list, not for "everything". A saving
    bought by deleting a real instruction is not a saving; it is a behaviour
    change with nothing pointing back at the commit that caused it. Two layers:

      1. A mechanical extractor ported from `zc6t`'s `fidelity_diff.py`, run
         against the vendored stock text. On THIS artifact it is thin — it
         extracts exactly two tokens, because the stock file states its rules
         in prose and fenced blocks rather than in inline code spans and
         ALL-CAPS imperatives. That thinness is the reason for layer 2.
      2. An explicit enumeration, `REQUIRED_RULES` + `REQUIRED_COMMANDS`. It
         pins the operating rules themselves — above all the resource-accounting
         rule, which has exhausted host disk before — not just the agent names.
         Rules are matched tolerantly (any accepted phrasing, normalised) so a
         faithful rewording survives; the two delegation forms are matched
         verbatim, because a paraphrased command is a broken command.

(d) BYTE STABILITY — the *precondition* for one cold head write, not the cache
    behaviour itself. A static test cannot observe `cache_read` on a live
    response. What it can prove is that the text carries no token whose value
    differs between two composions of the same head.

Pure-Python, filesystem-only: no network, no API key, no bundle load.
Run with `python3 -m pytest tests/ -q` from the repo root.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "lean-head-v1"
TARGET = "context/amplifier-tester-awareness.md"

# --- (b) the per-artifact budgets -------------------------------------------
#
# Chars, not bytes and not tokens — the published head census is in chars, so
# these can be added to it directly. Each is the MEASURED size, pinned.
LEAN_BUDGET_CHARS = 1242
STOCK_CHARS = 2068
SAVED_CHARS = 826

# --- (c) the citations, pinned so they cannot be quietly loosened -----------
NON_INFERIORITY_MARGIN_PP = -10.0  # frozen, SPEC.md 9.1
CITED_QUALITY_LOWER_BOUND_PP = -7.15  # model_performance-5zp, one-sided 95% LB
CITED_COST_DELTA_PCT = -13.57  # model_performance-g7h3 primary
CITED_COST_CI_PCT = (-22.27, -4.86)

# --- (c.2) rules that must survive every rewrite ----------------------------
#
# Deliberately keyed to the RULE, not to the wording. Each entry is a tuple of
# acceptable phrasings; at least one must appear (case-insensitively,
# whitespace-normalised) in the text under test. This matters: literals copied
# from the shipped lean text would fail on any faithful rewording, which would
# train the next author to edit this list instead of honouring it — and a rule
# check that gets edited away is not a rule check.
#
# The consequence, stated so nobody misreads the red-before run: THESE
# assertions pass against BOTH the stock text and the lean text, because both
# state the rules. The fail-before signal comes from the byte pin and the char
# budget, which is the honest signal — the pre-change file is not the measured
# lean text and is over budget; it is not missing its own rules.
REQUIRED_RULES: dict[str, tuple[tuple[str, ...], ...]] = {
    "scope of the bundle": (
        ("core, modules, bundles, foundation, app-cli",),
        ("before pushing to GitHub",),
        ("multi-repo changes",),
    ),
    # The routing rule. Without it this bundle gets pointed at ordinary user
    # software, which is reality-check's job, not a DTU's.
    "routing away from non-Amplifier software": (
        ("Do NOT use",),
        ("outside the Amplifier ecosystem",),
        ("amplifier-bundle-reality-check",),
        ("tell the user to get that bundle",),
        ("insist",),
    ),
    # THE ONE WITH A COST ATTACHED. Repeated setup-digital-twin delegations
    # accumulate environments; the sub-agent is stateless and cannot see its
    # siblings; the orchestrator therefore owns the ledger and the cap. This
    # has exhausted host disk. Pinning the agent names alone would not catch a
    # rewrite that dropped it.
    "resource accounting (orchestrator responsibility)": (
        ("resource accounting",),
        ("accumulate", "launches another DTU"),
        ("Gitea",),
        ("tears them down automatically", "torn down automatically"),
        ("stateless",),
        ("siblings",),
        ("across all delegations",),
        ("hard cap on concurrent environments",),
        ("live count",),
        ("remaining budget",),
        ("silently launch N environments",),
        ("exhaust host disk",),
    ),
}

# The two delegation forms, VERBATIM — a paraphrase here is a broken command,
# so these are matched exactly, not normalised.
REQUIRED_COMMANDS: tuple[str, ...] = (
    'delegate(agent="amplifier-tester:setup-digital-twin", '
    'instruction="<what the user needs>", context_depth="recent", '
    'context_scope="conversation")',
    'delegate(agent="amplifier-tester:validator", '
    'instruction="<DTU instance ID and what to check>", '
    'context_depth="recent", context_scope="agents")',
)

# --- (d) tokens that would break one-cold-head-write-per-session ------------
VOLATILE_PATTERNS = {
    "an absolute POSIX path": re.compile(r"(?<![\w`])/(?:home|root|tmp|Users)/"),
    "a Windows absolute path": re.compile(r"[A-Za-z]:\\\\"),
    "an ISO timestamp": re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}"),
    "a 40-hex sha": re.compile(r"\b[0-9a-f]{40}\b"),
    "a cache content-hash suffix": re.compile(r"-[0-9a-f]{16}\b"),
}

# --- the mechanical extractor, ported verbatim in behaviour from zc6t -------
CODE_SPAN = re.compile(r"`([^`\n]{2,80})`")
MENTION = re.compile(r"@[\w.-]+:[\w./-]+")
URL = re.compile(r"https?://[^\s)\]\"'>]+")
CAPS = re.compile(r"\b(MUST(?: NOT)?|NEVER|ALWAYS|REQUIRED|DO NOT|ONLY|STOP)\b")
CMD = re.compile(
    r"^\s*(?:\$ )?((?:npm|uv|pip|git|gh|python3?|make|brew|winget|adb|amplifier|"
    r"amplifier-[\w-]+|curl|docker|az)\s+[^\n|]{3,120})",
    re.MULTILINE,
)


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).casefold()


def extract_rules(stock: str) -> list[str]:
    found: list[str] = []
    for pattern in (CODE_SPAN, MENTION, URL, CAPS, CMD):
        for match in pattern.finditer(stock):
            token = (match.group(1) if pattern.groups else match.group(0)).strip()
            if len(token) >= 3:
                found.append(token)
    seen: set[str] = set()
    ordered: list[str] = []
    for token in found:
        key = _norm(token)
        if key not in seen:
            seen.add(key)
            ordered.append(token)
    return ordered


def _shipped() -> str:
    return (REPO_ROOT / TARGET).read_text(encoding="utf-8")


def _pinned_lean() -> str:
    return (FIXTURES / "amplifier-tester-awareness.md").read_text(encoding="utf-8")


def _pinned_stock() -> str:
    return (FIXTURES / "amplifier-tester-awareness.stock.md").read_text(encoding="utf-8")


class TestBytePinAgainstTheV1Head:
    """(a) The shipped file IS the measured V1 text, byte for byte.

    The acceptance criterion is equality with what the shim produced for
    variant v1, not with a prose description of it, so the reference is
    vendored rather than paraphrased. See `tests/fixtures/lean-head-v1/README.md`
    for provenance.
    """

    def test_shipped_file_is_byte_identical_to_v1(self) -> None:
        want = _pinned_lean()
        got = _shipped()
        assert got == want, (
            f"{TARGET} has drifted from the V1 lean head ({len(got)} chars vs "
            f"the pinned {len(want)}). The -13.57% cost reduction was measured "
            "against these exact bytes.\n"
            f"--- pinned v1 ---\n{want}\n--- shipped now ---\n{got}"
        )

    def test_the_v1_fixture_is_the_measured_size(self) -> None:
        """Guards the reference itself: an edited fixture proves nothing."""
        assert len(_pinned_lean()) == LEAN_BUDGET_CHARS

    def test_the_stock_fixture_is_the_measured_size(self) -> None:
        assert len(_pinned_stock()) == STOCK_CHARS


class TestCharBudget:
    """(b) The artifact stays at or below its shipped lean size."""

    def test_shipped_file_within_budget(self) -> None:
        actual = len(_shipped())
        assert actual <= LEAN_BUDGET_CHARS, (
            f"{TARGET} is {actual} chars, over its pinned lean budget of "
            f"{LEAN_BUDGET_CHARS} (+{actual - LEAN_BUDGET_CHARS}). This text is "
            "in the head of every session that loads the bundle, used or not. "
            "If the growth is a RULE that must be there, raise the budget in "
            "the same commit, add it to REQUIRED_RULES, and say why in the "
            "message — never silently."
        )

    def test_the_recorded_saving_has_not_moved(self) -> None:
        """The saving is a number in the repo, not a claim in a commit message."""
        assert STOCK_CHARS - LEAN_BUDGET_CHARS == SAVED_CHARS
        assert len(_pinned_stock()) - len(_pinned_lean()) == SAVED_CHARS


class TestFidelity:
    """(c) Every enumerated rule, command and pointer survives the rewrite."""

    @pytest.mark.parametrize("group", sorted(REQUIRED_RULES))
    def test_required_rules_survive(self, group: str) -> None:
        text = _norm(_shipped())
        missing = [
            " / ".join(alts)
            for alts in REQUIRED_RULES[group]
            if not any(_norm(alt) in text for alt in alts)
        ]
        assert not missing, (
            f"{TARGET} no longer states these {group} rules: {missing}. "
            "Fidelity beats compression at every point of conflict — a saving "
            "bought by deleting a real instruction is a behaviour change, not a "
            "saving."
        )

    def test_the_rule_check_is_wired_to_the_rules_not_the_wording(self) -> None:
        """The stock text must satisfy the same rule checks the lean text does.

        If it does not, the rules list has been written against one phrasing
        and has stopped testing the rule.
        """
        stock = _norm(_pinned_stock())
        for group, rules in REQUIRED_RULES.items():
            for alts in rules:
                assert any(_norm(alt) in stock for alt in alts), (
                    f"{group}: none of {alts} appears in the STOCK text, so this "
                    "entry is pinning a phrasing rather than a rule."
                )

    @pytest.mark.parametrize("command", REQUIRED_COMMANDS)
    def test_delegation_commands_survive_verbatim(self, command: str) -> None:
        assert command in _shipped(), (
            f"{TARGET} no longer carries this delegation form verbatim: "
            f"{command!r}. A paraphrased command is a broken command."
        )
        assert command in _pinned_stock(), (
            "This command is not in the stock text either — the pin is wrong."
        )

    def test_no_mechanically_extracted_stock_token_was_dropped(self) -> None:
        """Layer 1: zc6t's extractor, re-run here against the vendored stock.

        Deliberately noisy in one direction only: it over-reports (a
        compressed-but-preserved rule can be flagged) and under-reports never.
        On this artifact it yields two tokens — which is precisely why
        REQUIRED_RULES exists and is not optional.
        """
        stock, lean = _pinned_stock(), _shipped()
        lean_n = _norm(lean)
        missing = [r for r in extract_rules(stock) if _norm(r) not in lean_n]
        assert not missing, f"present in stock, absent from the shipped text: {missing}"

    def test_the_extractor_is_known_to_be_thin_here(self) -> None:
        """Pins the limitation itself, so nobody mistakes layer 1 for coverage."""
        assert len(extract_rules(_pinned_stock())) == 2


class TestByteStability:
    """(d) The precondition for one cold head write per session."""

    def test_shipped_file_carries_no_volatile_token(self) -> None:
        text = _shipped()
        offenders = [
            f"{label}: {match.group(0)!r}"
            for label, pattern in VOLATILE_PATTERNS.items()
            for match in [pattern.search(text)]
            if match
        ]
        assert not offenders, (
            f"{TARGET} contains a token that can differ between two composions "
            f"of the same head: {offenders}. Every such token forces a second "
            "cold head write and forfeits the Anthropic cache advantage."
        )

    def test_reading_the_file_twice_gives_the_same_bytes(self) -> None:
        assert _shipped() == _shipped()


class TestCitedResults:
    """The cited measurements this change ships on — pinned, never re-bought."""

    def test_cited_quality_lower_bound_clears_the_frozen_margin(self) -> None:
        assert CITED_QUALITY_LOWER_BOUND_PP > NON_INFERIORITY_MARGIN_PP, (
            f"The cited one-sided 95% LB ({CITED_QUALITY_LOWER_BOUND_PP} pp) no "
            f"longer clears the frozen margin ({NON_INFERIORITY_MARGIN_PP} pp). "
            "The margin is frozen, so it is the LB that must move, not it."
        )

    def test_the_frozen_margin_has_not_been_loosened(self) -> None:
        assert NON_INFERIORITY_MARGIN_PP == -10.0

    def test_the_cited_cost_effect_excludes_zero(self) -> None:
        """The reason this change ships at all: the CI does not straddle zero."""
        low, high = CITED_COST_CI_PCT
        assert low < CITED_COST_DELTA_PCT < high
        assert high < 0.0
