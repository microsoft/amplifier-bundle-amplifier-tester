# DONE-NOTE — lane `j1e6-ci-amplifier-tester`

**Item:** `model_performance-j1e6` (project `model_performance`) — the multi-lane
CI item, one lane per repo.
**Repo:** `microsoft/amplifier-bundle-amplifier-tester`
**Branch:** `lane/j1e6-ci-amplifier-tester` (from `origin/main` @ `40c9da3`)
**PR:** <https://github.com/microsoft/amplifier-bundle-amplifier-tester/pull/18>
**Terminal outcome:** **A — RESOLVED (shipped for landing).** Every deliverable is
**DONE**. The cap did not bind: authority $0, actual spend **$0.00**, so nothing
was left unbought and this is not branch B. Nothing was unreachable, so it is not
branch C.

Per the landing-stage rule, "the live system now has CI" is satisfied here as
"CI is demonstrated red-then-green and shipped for landing". The **merge is the
manager's next stage**, followed by their check that `main` HEAD reports a
successful check-run — *configured is not installed*.

---

## Deliverables

| # | Deliverable | State |
|---|---|---|
| 1 | `.github/workflows/ci.yml` running the real suite, ruff pinned, `push:main` + `pull_request:main`, no path filters / no error-suppressing directives / no exit-code-discarding fallback | **DONE** |
| 2 | BOTH run URLs quoted in the PR body; the RED one's job log shows the suite executing with a genuine **test** failure | **DONE** |
| 3 | Scratch PR closed and its branch deleted — **verified by remote read**, not assumed | **DONE** |
| 4 | A statement of what the suite actually covers (test count) | **DONE** — 18 real tests, not an import smoke |
| 5 | If clean main is red: stop, report, fix as separate named commits | **DONE (did not trigger)** — clean main was **green** on the gate as wired |
| 6 | Draft PR, marked ready when the GREEN run is in; **not merged** | **DONE** |
| 7 | DONE-NOTE at the lane artifact root, never the repo root | **DONE** (this file) |

---

## 1. The workflow

`.github/workflows/ci.yml`, workflow commit **`dafb46e`** — workflow-only, adds
no other file to the repo — plus **`7beed61`**, a **comment-only** amendment (no
job, step, trigger or command change; see the `enable-cache` bullet below). Three job definitions → **four checks** on `push: main`
and `pull_request: main`:

| Check | Command |
|---|---|
| **Lint** | `uvx ruff@0.16.6 check --isolated --select E4,E7,E9,F .` |
| **Tests (Python 3.11)** / **(3.13)** | `uv run --isolated --no-project --python <v> --with pytest==9.1.1 python -m pytest tests/ -q --tb=short` |
| **Bundle structure (YAML)** | inline PyYAML parse of `bundle.md` frontmatter, `behaviors/*.yaml`, and the shipped DTU profiles under `.amplifier/` |

Choices, and why:

- **ruff PINNED to 0.16.6**, `--isolated`, `--select E4,E7,E9,F` — the same pin
  and rule set as the sibling bundles `wayfinder` and `browser-tester`. Pinned so
  a future ruff release cannot turn this red without a visible edit to this file;
  `--isolated` so a `[tool.ruff]` config added later cannot quietly change what
  the gate means.
- **pytest PINNED to 9.1.1** — it *defines* the gate, so it is pinned. There is
  no peer dependency to float here: the suite is pure-Python and filesystem-only
  (no network, no API key, no bundle load), so pytest is the entire dependency
  list.
- **The standing test command is honored verbatim.** There is no Makefile and no
  check target in `AGENTS.md`; the suite's own module docstring says *"Run with
  `python3 -m pytest tests/ -q` from the repo root"*, so that docstring **is** the
  standing command, and CI runs exactly it.
- **`--no-project` / `--isolated`** — no `pyproject.toml`, no `uv.lock`, nothing
  for uv to sync.
- **No `enable-cache:` on `setup-uv`** — and the reason is a **disputed
  measurement**, recorded as one rather than asserted as fact (commit `7beed61`
  fixes exactly that overreach in the original comment). `enable-cache: true`
  keys a cache on `**/uv.lock`; this repo commits no lockfile. One sibling lane
  (`wayfinder`) observed that hard-fail setup before ruff or pytest ran — a red
  that proves nothing. Another (`ios-tester`) measured the same input as harmless
  on a newer `setup-uv`. **Neither measured it here.** Omitting the input is
  correct under either reading, and these jobs install a handful of small wheels,
  so the disagreement did not need resolving to ship. (Separately:
  `enable-caching:` is not a valid input at all and is silently ignored, so
  "correcting" that spelling into `enable-cache:` in a lockfile-less repo
  converts a no-op into the disputed failure mode. Neither form is used here.)
- **No LLM-backed validation.** `.amplifier/evaluations/` launches a Digital Twin
  Universe and spends real money per run; it is deliberately not wired into a
  push gate. CI minutes only, `permissions: contents: read`, no secrets.
- **The DTU profiles are added to the structure check** beyond the sibling
  template. They are YAML this bundle ships, and a malformed one currently fails
  only when a user launches an environment.

**Forbidden constructs: absent from the file entirely, including from prose.**
`grep -nEi 'continue-on-error|\|\| true|paths:|paths-ignore'` returns no match —
the comments are worded to avoid the literal tokens, so a reviewer's grep is
unambiguous rather than turning up a mention and needing a human to adjudicate it.

## 2. What the suite actually covers — 18 real tests, **not** an import smoke

`tests/test_lean_head_guardrail.py` is the lean-head drift guardrail for
`context/amplifier-tester-awareness.md`. It landed in **#16 (`40c9da3`)** — *minutes
before this lane opened* — and **was executed by nothing**. This workflow is what
executes it. Its 18 tests assert:

- **byte pin** — the shipped file is byte-identical to the measured v1 lean head,
  vendored verbatim under `tests/fixtures/lean-head-v1/`; the fixtures are
  themselves size-guarded, so an edited reference cannot pass;
- **char budget** — 1,242 chars, pinned **per artifact** (never a whole-head
  absolute);
- **fidelity** — an enumeration of rules that must survive any rewrite, including
  the resource-accounting rule that has exhausted host disk, plus both
  `delegate(...)` forms matched **verbatim**;
- **byte stability** — no volatile token (absolute path, ISO timestamp, 40-hex
  sha, cache hash) that would force a second cold head write;
- **cited results** — the frozen −10 pp non-inferiority margin and the cited
  −13.57 % cost effect cannot be quietly loosened.

So the green run is a green run over something. That statement is in the PR body
too, because a test count nobody can see is indistinguishable from decoration.

## 3. Red-then-green — proven, not assumed

**RED:** <https://github.com/microsoft/amplifier-bundle-amplifier-tester/actions/runs/34156005850>
(scratch PR **#17**, since closed)

Scratch branch `ci/red-proof-j1e6` carried the workflow plus **one deliberate
defect per job**, so each job is proven to bite *for its own reason* rather than
one failure masking the rest:

```
Tests (Python 3.11)  Run the standing test command   1 failed, 18 passed in 0.05s
Tests (Python 3.13)  Run the standing test command   1 failed, 18 passed in 0.04s
Lint                 Lint (ruff, pinned)             F821 Undefined name `this_name_is_not_defined_anywhere`
Bundle structure     Parse bundle.md frontmatter...  - behaviors/amplifier-tester.yaml: while parsing a flow sequence
                                                       expected ',' or ']', but got '<stream end>'
```

The test job's red is **`1 failed, 18 passed`** — a genuine *test* failure inside
a suite that **collected and executed**, on both Pythons. Not a setup error, not
a lint error, which is the whole point of the gate: a red from a broken runner
proves nothing about the workflow.

**GREEN:** <https://github.com/microsoft/amplifier-bundle-amplifier-tester/actions/runs/34156147826>
— all four checks pass on the workflow-only commit `dafb46e`. The two later
commits are green too: `21b9285` (lane artifacts only)
<https://github.com/microsoft/amplifier-bundle-amplifier-tester/actions/runs/34156334504>
and `7beed61` (comment-only)
<https://github.com/microsoft/amplifier-bundle-amplifier-tester/actions/runs/34156499023>.

```
Lint                     All checks passed!
Tests (Python 3.11)      18 passed in 0.03s
Tests (Python 3.13)      18 passed in 0.03s
Bundle structure (YAML)  4 YAML document(s) parsed.  Bundle structure OK.
```

Both job logs are committed verbatim under `evidence/`.

**Scratch PR closed, branch deleted — VERIFIED BY REMOTE READ.** Not by trusting
a success message: `git ls-remote --heads origin ci/red-proof-j1e6` returns **0
lines**, and the branch is absent from the full `git ls-remote --heads origin`
listing. `gh pr view 17` reports `state: CLOSED`. The local checkout was moved off
the scratch branch *before* deleting it, since `--delete-branch` aborts on a
worktree that still has it checked out — the exact failure a sibling lane hit,
where trusting the reported close would have left the scratch branch on the
remote.

## 4. Clean main was GREEN on the gate — stop-and-report did not trigger

Run against clean `main` @`40c9da3` **before** the workflow was written
(`evidence/local-preflight-clean-main.txt`): `ruff@0.16.6 check --isolated
--select E4,E7,E9,F .` → *All checks passed!*; `pytest tests/ -q` → *18 passed*
on 3.11 and 3.13. So no findings to fix, and nothing was weakened to get green.

Two things sit deliberately **just outside** the gate, reported rather than hidden:

1. `ruff format --check` would reformat **2 files** —
   `tests/test_lean_head_guardrail.py` and
   `.amplifier/evaluations/01-setup-with-build-up-foundation/metrics/extract_metrics.py`.
   Reformatting source is out of scope for a workflow-only PR.
2. Ruff's **full default rule set** (no `--select`) reports **6 findings**, all
   style tiers (ISC004 and friends), none of them breakage.

Neither is worked around by narrowing the selection: the selection *is* ruff's own
classic default tier, and the delta above it is stated in the PR body in full.

## 5. Spend

**$0.00 against the $0 authority.** The authority's arithmetic — 0 runs × 0 arms
× $0 / 1.00 = $0.00, slack $0.00 — closes trivially and correctly for a lane that
buys no runs: CI minutes only. **No API calls, no DTU, no containers, nothing
registered in the infra ledger, nothing to tear down.** Two gating runs × 4
checks, each job seconds long.

---

## FINDINGS

### F1 — GOAL DEFECT (already reported once by a sibling lane; reproduced here)

This item is **deliberately one item with nineteen lanes**, but its per-lane goal
template applies a **single-lane claim/resolve procedure** to it:

- Procedure 1 says a refused claim means *write BLOCKED.md and stop*.
- Procedure 5 ends in `work_resolve`.

On a one-item/many-lanes item **at most one lane can ever hold it**, so every
other lane is instructed to declare itself BLOCKED over a claim refusal that is
the **designed steady state**. Obeyed literally by all 19 CI lanes, the owner
directive would have produced 19 `BLOCKED.md` files and no CI.

**Four lanes have now filed this independently** — `browser-tester`, `notify`,
`tool-filesystem`, `ios-tester` — with two of them filing self-corrections purely
to fix their own undercount of how many lanes had hit it. This lane is the fifth.
Four-of-four (now five-of-five) is a systematic defect in the per-lane template
for multi-lane items, not a coincidence.

What this lane did instead, matching the sibling lanes' recorded precedent: read the authoritative spec with `work_list(item_id=...)` —
which returns the full description and acceptance criteria **without claiming** —
completed every deliverable, and reported the defect. `work_claim` was attempted
first and refused (*"already claimed by agent-spark-1-1101253"*); the item's
status is in fact already `resolved`, over a resolution covering **1 of 19**
repos.

Branch C was rejected on the merits: the outcome was not unreachable — it is
delivered, and sits in an open PR. A `BLOCKED.md` here would have been false.

**Fix, either way works:** file one item per repo, **or** have the goal say — *claim
if free; if a sibling holds it, proceed and record per-repo completion, and let
the holder or the manager resolve once every lane has landed.*

### F2 — how this lane's completion is recorded on the item

`work_resolve` is not available: this session does not hold the item, and the item
is already resolved with different text (which fails loudly rather than silently
echoing the old text back — the correct behaviour). `work_reopen` would clear
`closed_at` and move every throughput roll-up by one item, which is the manager's
call and not a lane's.

So this lane's slice is appended with **`work_erratum`** — append-only, needs no
claim, never rewrites the stored resolution, and travels with the item everywhere
its resolution is shown. That is the sanctioned mechanism for *the record is
incomplete, the work stands*.

### F3 — transferable to the remaining CI lanes

1. **`setup-uv` caching in a lockfile-less repo — and a live disagreement about
   it.** `wayfinder` observed `enable-cache: true` hard-fail (*"No file matched to
   [**/uv.lock]"*); `ios-tester` measured it harmless on a newer `setup-uv`. This
   lane measured **neither** — it omitted the input, which is correct under both
   readings, and says so in the file rather than repeating an inherited claim as
   fact. What is *not* in dispute: `enable-caching:` is not a valid input and is
   silently ignored, so a lane that "fixes" that spelling in a lockfile-less repo
   converts a no-op into the contested failure mode.
2. **Word the workflow's comments to avoid the forbidden tokens themselves.**
   Saying *"no `continue-on-error`"* in a comment puts `continue-on-error` in the
   file, and the reviewer's grep cannot tell prose from configuration. Phrase it
   as *"no error-suppressing job or step directive"* and the grep stays clean.
3. **Move off the scratch branch before deleting it.** `gh pr close
   --delete-branch` reports the close even when the branch deletion aborts on a
   worktree conflict; verify with `git ls-remote`, never with the success message.
4. **Give each job its own deliberate defect in the red proof.** One failing test
   proves only the test job. Three defects in one scratch commit prove all four
   checks bite, for one run's cost.

---

## What remains open (for the manager)

1. **Merge PR #18** — the lane never merges.
2. After merging, confirm `main` HEAD reports a successful check-run
   (`gh api repos/microsoft/amplifier-bundle-amplifier-tester/commits/main/check-runs`).
   *Configured is not installed.*
3. Decide the item-level bookkeeping for `model_performance-j1e6` (F1/F2): it reads
   `resolved` over a directive that is a handful of nineteen repos done.
