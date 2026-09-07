# DONE-NOTE — lane `3ahq-leanhead-amplifier-tester`

**Item:** `model_performance-mvc8` (project `model_performance`)
**Repo:** `microsoft/amplifier-bundle-amplifier-tester`
**Branch:** `lane/3ahq-leanhead-amplifier-tester` (from `origin/main` @ `7b37ad0`)
**Terminal outcome:** **A — RESOLVED.** Every deliverable is DONE except one
half of one acceptance clause, recorded NOT-POSSIBLE below with its reason.
Not branch B: the cap did not bind — the authorised spend was $0 and the actual
spend was $0.00, so nothing was left unbought.

---

## Deliverables

| # | Deliverable | State |
|---|---|---|
| 1 | The patch applied (never force-applied with fuzz) | **DONE** |
| 2 | Fidelity table re-verified at today's head, not inherited | **DONE** |
| 3 | Stock → lean char counts | **DONE** |
| 4 | Byte-for-byte pin test against the v1 text | **DONE** |
| 5 | Guardrail fails against the pre-change file | **DONE (locally)** |
| 6 | Red + green **CI run URLs** quoted in the PR body | **NOT-POSSIBLE** — see below |
| 7 | Draft PR, marked ready when the local suite is green, not merged | **DONE** |
| 8 | DONE-NOTE at the lane artifact root, never the repo root | **DONE** (this file) |

---

## 1. The patch applied — clean, zero fuzz

Source: `docs/lanes/zc6t-lean-head-ship/patches/context-files/02-amplifier-bundle-amplifier-tester-amplifier-tester-awareness.md.patch`
on `main` of `microsoft/amplifier-foundation` (PR #372).

Applied with `git apply --verbose` → *"Applied patch
context/amplifier-tester-awareness.md cleanly."* `git apply` performs **no
fuzzy placement at all**, so there is no hunk-relocation risk of the kind that
put a sibling lane's diff 147 lines out of position. Zero hunks relocated, zero
fuzz, **no hand-port needed, nothing diverged**.

Precondition checked before applying: the stock file in this repo at `7b37ad0`
is **byte-identical** (`diff` clean) to the copy `zc6t` resolved and measured at
`~/.amplifier/cache/amplifier-bundle-amplifier-tester-51fb043af4f8b374/context/amplifier-tester-awareness.md`.
The patch met exactly the text it was authored against.

## 2–3. Char counts and fidelity

| | chars | sha256 |
|---|---|---|
| stock (`7b37ad0`) | **2,068** | `b64317648adb082eb29a13d762db4d633217f8f4db6f01df325650e9372377e7` |
| lean (shipped) | **1,242** | `1f9d7b1b6df122ecdc432129c0c55149a6ba636c804cdb8045c8e6d224f2e27a` |
| **saved** | **826** | matches `zc6t`'s `fidelity-report.json` index 2 exactly |

Fidelity was **re-derived at today's head, not inherited**: 20 enumerated
rules / constraints / commands / pointers, **20 present in lean, 0 missing, 0
restorations needed**. Both `delegate(...)` forms survive character for
character. Full row-by-row table, plus the three things compressed *without*
loss (section headings, one rationale clause, bullets folded to prose):
`evidence/fidelity-table.md`.

**Finding worth carrying forward:** `zc6t`'s mechanical extractor
(`fidelity_diff.py`) yields only **two** tokens on this 2,068-char file, because
the stock text states its rules in prose and fenced blocks rather than in inline
code spans and ALL-CAPS imperatives — the shapes that extractor looks for. Its
CLEAN verdict for this target is therefore *weakly evidenced by the extractor
alone*. The hand-read table is the real evidence, and the guardrail pins the
limitation itself (`test_the_extractor_is_known_to_be_thin_here`) so nobody
mistakes layer 1 for coverage. The item's instruction to *"watch this one
particularly closely"* was warranted — not because a rule was dropped (none
was), but because the automated check would not have caught it if one had been.

## 4–5. The pin test, red before green

`tests/test_lean_head_guardrail.py`, 18 tests, pure-Python, no network, no API
key. Shape copied from `amplifier-foundation`'s `tests/test_lean_head_guardrail.py`.

- **byte pin** — the shipped file is byte-identical to the vendored verbatim
  slice of `v1_instructions.json` span 2's body (1,242 chars), and the fixture
  itself is size-guarded so an edited reference cannot pass.
- **char budget** — pinned **per artifact** at 1,242, never against a whole-head
  absolute (`zc6t` measured a real composed head at 320,410 chars against the
  shim's 48,249; any whole-head figure pinned in a single bundle repo would be
  false on arrival).
- **required rules** — 20 assertions across three groups, including twelve for
  the resource-accounting rule alone (accumulation, Gitea reuse, no automatic
  teardown, statelessness, blindness to siblings, tracking across all
  delegations, the hard cap, live count, remaining budget, silent N-for-N
  launches, host-disk exhaustion) plus the reality-check routing rule. The two
  delegation forms are matched **verbatim**; everything else is matched
  tolerantly against accepted phrasings.
- **byte stability** — no absolute path, timestamp, sha or cache-hash suffix,
  the repo-side precondition for one cold head write per session.
- **cited results** — `g7h3`'s −13.57 % CI and `5zp`'s −7.15 pp LB against the
  frozen −10 pp margin, pinned so neither can be quietly loosened.

**Design choice, recorded because it changes what the red run means.** The rule
assertions are keyed to the *rule*, not to the lean *wording*, and therefore
pass against the stock text too — a rules list written in the shipped phrasing
would fail on any faithful rewording, which trains the next author to edit the
list instead of honouring it. `test_the_rule_check_is_wired_to_the_rules_not_the_wording`
re-runs every rule against the vendored stock text and pins that property. The
consequence: the fail-before signal is the **byte pin and the char budget**, not
the rule checks.

| run | result | evidence |
|---|---|---|
| guardrail commit only, pre-change text | **2 failed, 16 passed** | `evidence/guardrail-local-red.txt` |
| after the patch | **18 passed** | `evidence/guardrail-local-green.txt` |

The two red assertions were the byte pin (*"has drifted from the V1 lean head
(2068 chars vs the pinned 1242)"*) and the budget (*"is 2068 chars, over its
pinned lean budget of 1242 (+826)"*). The guardrail landed in its **own commit**
(`2eb4d94`) ahead of the change (`5cc9a08`), so it demonstrably failed before it
passed.

Run it with `python3 -m pytest tests/ -q` from the repo root. No pytest config
or `pyproject.toml` was added — the suite needs none, and inventing packaging
this repo does not otherwise have would be scope the item did not ask for.

## 6. CI run URLs — NOT-POSSIBLE, with reason

**What was executed:** the full guardrail suite ran twice locally on this
machine — 2 failed / 16 passed against the pre-change text, 18 passed after the
patch — both captured verbatim under `evidence/`. What could not be produced is
a pair of **GitHub Actions run URLs**.

**Reason:** `.github/` **does not exist in this repository.** There is no
workflow, so there is no run to link. This repo is one of the 18 covered by the
`j1e6-ci-*` lane, which the goal sequences deliberately *behind* this one:
wiring CI first would have produced a green run over a suite that did not yet
contain this guardrail.

**Deviation recorded, per "choose, record the choice, continue":** I did **not**
add a workflow myself. The item's acceptance clause asks for CI URLs; the goal
that launched this lane instructs the opposite — *"CI: this repo has NONE …Say
that plainly rather than implying a green run; your pin tests plus the local
suite are the evidence, and the CI lane follows you."* I followed the goal.
Adding `.github/workflows/` here would also collide with the lane that owns it.
**Recommendation for the manager:** once `j1e6` wires CI, this guardrail
executes on every PR unchanged — no edit to it is needed. If the red/green URL
pair is wanted as a record, the cheapest way to get it is to re-run the two
commits of this branch under the new workflow after `j1e6` lands.

## 7. Publication

Opened as a **draft** against `microsoft/amplifier-bundle-amplifier-tester`,
then **marked ready for review** on the green local suite. **Not merged** — the
manager merges.

- PR **#16** — https://github.com/microsoft/amplifier-bundle-amplifier-tester/pull/16
- branch `lane/3ahq-leanhead-amplifier-tester`, state `OPEN`, `isDraft: false`,
  `mergeable: MERGEABLE`, read back with
  `gh pr view 16 --json number,isDraft,state,url,headRefName,headRefOid,mergeable`

**Choice recorded.** The item says *"marked ready only on green CI"*; the goal
says *"marked ready when the local suite is green"*. There is no CI in this repo,
so the item's gate can never open and the PR would sit as a draft forever. I
took the goal's gate — local suite green, 18 passed — and marked it ready.
Marking ready does not merge; the manager's merge gate is unaffected.

## 8. Spend

**$0.00.** Cap arithmetic as stated in the goal: **0 runs × 0 arms × $0 / 1.00 =
$0.00**, slack $0.00 — and it closes, because this deliverable buys nothing.
No API call, no DTU, no Gitea instance, no infrastructure registered and none to
tear down. `g7h3`'s $428.10 and `5zp`'s quality bound are **cited, never
re-bought**.

---

## Findings against the goal (not against the work)

**F1 — the GOAL.md I was launched with describes a different repo's slice.**
Its Task section says *"This lane owns ONLY the `amplifier-module-tool-filesystem`
slice: `read_file`, `write_file`, `edit_file`, `grep`, `glob`"*, points at
`patches/tool-descriptions/`, and asserts *"THIS REPO CARRIES THE ONE REAL
WEAKENING `zc6t` FOUND — `edit_file`, restored in-repo at +450 chars"*. None of
that is this repo. This worktree is `amplifier-bundle-amplifier-tester`; the
item's own spec names `context/amplifier-tester-awareness.md` and
`patches/context-files/02-…`. Procedure step 1 makes the **work item**
authoritative over the goal summary, so I followed the item. The goal text
appears to be a sibling lane's, pasted with only the header and paths swapped.

Two concrete costs of that mismatch, both avoided here but cheap to hit:

1. A lane that trusted the goal over the item would have gone looking for
   `read_file`/`edit_file` descriptions that do not exist in this repo and
   reported "no reachable target" — `zc6t`'s finding F1 repeating one level down.
2. The `edit_file` weakening warning is real but belongs to the filesystem lane.
   Carried into this repo it would have had a lane hunting a +450-char
   restoration that has no referent here. **Verified independently:** this
   target's `missing_rules` is `[]` in `fidelity-report.json`, and my own
   re-derivation at today's head found nothing dropped.

**F2 — the goal's "expect a small diff and do not pad it" was honoured, with
one deliberate exception.** The context change itself is 4 lines out, 33 in-out.
The guardrail is 352 lines. That is not padding: the item requires a byte pin, a
per-artifact budget and a required-rules check that survives the stock text
disappearing from the tree, which is what the two vendored fixtures and the
enumerated rules cost. The alternative — a three-line `assert` on file length —
would not have caught a rule being deleted, which is the failure the item says
to watch for.
