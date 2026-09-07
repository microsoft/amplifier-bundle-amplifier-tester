# Lane dae2-catalog-amplifier-tester — delegate-catalog SOURCES sweep

**Work item: `model_performance-pnn2`** (per-repo child of `model_performance-dae2`, filed and
claimed by this lane) · **Outcome branch: A (RESOLVED at the draft PR)** · **API spend: $0.00
measured, see §8**

Both agents' `meta.description` is now trigger-first, ≤600 chars, carries an explicit
USE WHEN / DO NOT USE WHEN, and contains **zero** `<example>`/`<commentary>` blocks.
Frontmatter only — both bodies are md5-identical to stock.

---

## 0. The parent item names six repos; this lane is one of them

`GOAL.md` Procedure 1 says to claim `model_performance-dae2`. That item is **one item covering
six repos**, worked by parallel lanes, so a lane that holds it for its whole run blocks the other
five. The claim succeeded, and the lane executed the recovery pattern the goal itself names
(precedent: `model_performance-k75p`, and `model_performance-slee`'s *"file ONE CHILD ITEM PER
REPO under this item, so each lane claims its own id"*):

| Step | Result |
|---|---|
| `work_claim item_id=model_performance-dae2` | claimed — the parent is a 6-repo container |
| `work_add` a per-repo child, `related: relates-to dae2` | **`model_performance-pnn2`** created |
| `work_release model_performance-dae2` | parent returned to the queue for the other five lanes |
| `work_claim item_id=model_performance-pnn2` | claimed, custody established |

**Reported, not absorbed:** `GOAL.md` should name a per-repo child id rather than the shared
parent. `dae2`'s own description already asks for per-repo lanes; the goal template has not caught
up.

---

## 1. The baseline was re-derived, and it had drifted

`GOAL.md` and `dae2` both quote **~2,981 chars** for this repo, with an explicit instruction to
verify rather than trust it. Verified against **`origin/main` @ `3ffbcd4`**, the current tip:

- The lane branch was cut from an older `main` and was **2 commits behind** (`40c9da3` lean-head
  guardrail, `3ffbcd4` CI). Rebased onto `3ffbcd4` before anything was measured, so every number
  below is against the current tree.
- Measured stock total: **2,907 chars**, not 2,981 — a **74-char** over-count in the census.
- Agent set confirmed as exactly two, by `validate-agents`' own discovery phase, not by eye:
  `candidates_scanned: 2`, `total_count: 2`, `location_counts: {"agents/": 2}`,
  `non_agent_count: 0`.

Counts are of the **parsed** YAML scalar. Both descriptions are `|` literal blocks, so each
includes the one trailing newline the block appends — measured identically on both sides.

---

## 2. Before / after

| File (`meta.description`) | stock | lean | delta | ≤600 |
|---|---:|---:|---:|:--:|
| `agents/setup-digital-twin.md` | 1,565 | **595** | −970 (−62.0 %) | yes |
| `agents/validator.md` | 1,342 | **592** | −750 (−55.9 %) | yes |
| **repo total** | **2,907** | **1,187** | **−1,720 (−59.2 %)** | |

`<example>` blocks **4 → 0**. `<commentary>` blocks **0 → 0**.
Evidence: `evidence/description-measurements.txt`.

**Nothing was edited that did not need it.** Neither description was trigger-first, both carried
example blocks, and both were over the 1,200-char structural-ERROR line — so both had to change.
No other file in the repo registers a delegate-catalog row, so there was nothing else in scope to
leave alone.

### Why this is worth doing at all

`meta.description` is **pay-per-turn**: it rides the `delegate` tool schema in every request of
every session that mounts this bundle, whether or not the agent is ever spawned. The agent body is
**pay-per-use** — read only when the agent actually runs. Stock spent 1,116 of its 2,907 chars on
four worked delegation examples, charged to every turn to serve the one turn that delegates.

**Not claimed here:** a rendered before/after `delegate` catalog capture. `GOAL.md`'s CENSUS SAFETY
clause forbids running `amplifier` on this host with a scratch `AMPLIFIER_HOME` — it silently
rewrites the real install's editable `.pth` files, which has happened for real in this program.
The sibling `kp79` lane's `render_catalog.py` builds exactly such a scratch session, so it was
**not** run. The measurement above is static (parsed source strings), which the same clause names
as the sanctioned method. The char delta is therefore a source-side figure; the catalog-side
figure would differ only by the renderer's fixed per-row framing.

---

## 3. FIDELITY TABLE — every stock fact, checked against lean

Method: enumerate every trigger / constraint / USE WHEN fact in each stock description, **including
facts that lived only inside the `<example>` blocks**, and locate each in the lean description.

**Result: zero triggers, constraints or USE WHEN / DO NOT USE WHEN facts lost. Nothing owed.**
Five facts that existed only inside example blocks were **rescued into the description proper**.
Two non-protected absences are listed separately in §3c with their restoration cost, rather than
netted away.

### 3a. `setup-digital-twin` (1,565 → 595)

| # | Stock fact | Lived in | In lean? |
|---|---|---|---|
| 1 | sets up **Digital Twin Universe** environments | lead | yes — "an isolated Digital Twin Universe (DTU) container" |
| 2 | for validating **Amplifier ecosystem changes** | lead | yes — "local changes to Amplifier ecosystem repos … need testing" |
| 3 | **mirrors changed repos to Gitea** | lead | yes — "Mirrors them to Gitea" |
| 4 | generates **Amplifier-specific DTU profiles** | lead | yes — verbatim ("the Amplifier-specific DTU profile") |
| 5 | `pypi_overrides` | lead + authoritative | yes — "pypi_overrides for amplifier-core" |
| 6 | `url_rewrites` | lead + authoritative | yes — "url_rewrites for modules/bundles/foundation" |
| 7 | **launches** the environment | lead | yes — "launches … it" |
| 8 | **verifies it works** | lead | yes — "verifies it end-to-end" |
| 9 | trigger: testing **local** changes | USE-WHEN para | yes — "local changes" |
| 10 | scope: **core, modules, bundles, foundation, app-cli** | USE-WHEN para | yes — verbatim list |
| 11 | in an **isolated container** environment | USE-WHEN para | yes — "isolated … container" |
| 12 | **before merging** | USE-WHEN para | yes — verbatim |
| 13 | authoritative: **Gitea mirroring** | authoritative | yes — same clause as #3 |
| 14 | authoritative: `pypi_overrides` **for amplifier-core** | authoritative | yes — verbatim |
| 15 | authoritative: `url_rewrites` **for modules/bundles/foundation** | authoritative | yes — verbatim |
| 16 | authoritative: **multi-repo change coordination** | authoritative | yes — "several repos at once" |
| 17 | authoritative: **end-to-end DTU launch and verification** | authoritative | yes — "launches and verifies it end-to-end" |
| 18 | *(example-only)* the instruction must **name the repo path(s)** | `<example>` 1 & 2 | yes — **RESCUED**: "Name the repo paths in the instruction." |
| 19 | *(example-only)* **several repos validated together** in one setup | `<example>` 2 | yes — **RESCUED**: "several repos at once" (stock's authoritative line said only "multi-repo change coordination") |
| 20 | DO NOT USE WHEN | — | **ADDED** — stock had none |

### 3b. `validator` (1,342 → 592)

| # | Stock fact | Lived in | In lean? |
|---|---|---|---|
| 1 | runs **post-launch validation checks** | lead | yes — "already launched and needs checking" + the check list |
| 2 | inside an **existing** DTU environment | lead | yes — "a Digital Twin Universe (DTU) is **already launched**" |
| 3 | verify **Amplifier ecosystem changes work correctly** | lead | yes — "to confirm Amplifier ecosystem changes work" |
| 4 | trigger: **after `setup-digital-twin` has launched a DTU** | USE-WHEN para | yes — "right after setup-digital-twin hands it off" |
| 5 | executes checks **keyed to the change type** | USE-WHEN para | yes — verbatim |
| 6 | change types: **core, module, bundle, CLI, foundation** | USE-WHEN para | yes — "(core version, module loading, bundle availability, CLI, foundation)" |
| 7 | **reports pass/fail results** | USE-WHEN para | yes — "pass/fail reported" |
| 8 | authoritative: **post-launch DTU validation checks** | authoritative | yes — same clause as #1 |
| 9 | authoritative: **Amplifier installation verification** | authoritative | yes — "Amplifier installed" |
| 10 | authoritative: **change-type-keyed smoke tests** | authoritative | yes — "full-stack smoke test" + "checks keyed to the change type" |
| 11 | authoritative: **module loading** | authoritative | yes — verbatim |
| 12 | authoritative: **bundle availability** | authoritative | yes — verbatim |
| 13 | authoritative: **CLI smoke testing** | authoritative | yes — "full-stack smoke test" + "CLI" |
| 14 | *(example-only)* the instruction must carry the **DTU instance ID** | `<example>` 1 & 2 | yes — **RESCUED**: "Name the DTU instance ID … in the instruction." |
| 15 | *(example-only)* the instruction must carry the **change types** | `<example>` 1 & 2 | yes — **RESCUED**: "… and change types in the instruction." |
| 16 | *(example-only)* **several change types in one validation run** | `<example>` 2 | yes — **RESCUED**: "several types per run" |
| 17 | DO NOT USE WHEN | — | **ADDED** — stock had none |

Both rescued instruction-shape facts (#14, #15) are also the agent body's own **required** inputs
(`validator.md` § Inputs: DTU instance ID *required*, change types *required*) — so stock stated a
requirement only inside an example a router never reads twice. The lean row states it in the row
itself.

### 3c. Absent from lean — assessed as NOT in the protected set, restoration cost quoted

`GOAL.md`'s fidelity gate protects *"any USE WHEN / DO NOT USE WHEN fact, trigger condition, or
constraint"*. Two stock items are absent and are not members of that set. Listed with their exact
restoration cost so a reviewer can overrule with a number in hand.

| Stock item | Why it is not a protected fact | Restoration cost |
|---|---|---|
| the `**Authoritative on:**` heading itself | A section label, not a fact. Every item it introduced is present (rows 13–17 / 8–13 above). Removing the label removes no routing information. | +23 chars ×2 |
| `context_depth="recent"` / `context_scope="conversation"\|"agents"` from the four example blocks | Delegation **call parameters**, not routing conditions — they say how to phrase the call once the routing decision is already made. **Checked, not assumed:** both delegation forms survive **verbatim** in `context/amplifier-tester-awareness.md`, which is always-on, and are pinned there byte-for-byte by `tests/test_lean_head_guardrail.py`'s `REQUIRED_COMMANDS`. Nothing is lost from the repo. | +62 chars, which would put `setup-digital-twin` at 657 and `validator` at 654 — both over the ERROR-adjacent cap |

### 3d. What the lean rows gained

- A **DO NOT USE WHEN** clause on both, which stock had on neither. Each names the agent or bundle
  that *should* get the work — `validator` ↔ `setup-digital-twin` for the near-miss inside this
  bundle, and `reality-check` for the near-miss outside it (the routing rule already stated in
  `context/amplifier-tester-awareness.md`).
- Five example-only facts promoted into the row a router actually reads.

So the lean rows carry **more routing information than stock** at 59 % fewer chars.

---

## 4. Bodies byte-identical

Only the `meta.description` scalar changed. `meta.name` and `model_role` are untouched
(`[reasoning, coding, general]` and `[coding, general]` respectively), and every byte after the
closing `---` is unchanged:

| File | body md5, stock | body md5, branch | |
|---|---|---|:--:|
| `agents/setup-digital-twin.md` | `356318140ab85709b867bc6f8e3dcaca` | `356318140ab85709b867bc6f8e3dcaca` | equal |
| `agents/validator.md` | `4f59c94bd44e4e011dd3c594ba83c99a` | `4f59c94bd44e4e011dd3c594ba83c99a` | equal |

"Stock" is `origin/main` @ `3ffbcd4`, extracted with `git archive` into a scratch tree — not the
working tree, and not a cached copy that could have drifted.

---

## 5. `validate-agents` — fail before, pass after

Recipe: `foundation:recipes/validate-agents.yaml` **v1.8.0**. Its gates: any
`<example>`/`<commentary>` in a description is a structural ERROR (V3), description length WARN
> 600 chars / ERROR > 1,200 (V5).

### 5a. Deterministic phases (0–3), both trees — `$0`, no LLM

`evidence/validate-agents-structural-phases.txt`, produced by executing the recipe's own
bash/python heredocs verbatim (runner ported from the `kp79` lane, so it cannot drift from the
recipe):

```
--- STOCK (origin/main 3ffbcd4) ---
agents discovered: 2
structural summary: {'total': 2, 'passed': 0, 'errors': 4, 'warnings': 2}
quality_level: critical
  setup-digital-twin  chars=1565 examples=2 errors=['DESCRIPTION_EXCESSIVE', 'EXAMPLE_BLOCK_PRESENT'] warnings=['NO_TOOLS_SECTION']
  validator           chars=1342 examples=2 errors=['DESCRIPTION_EXCESSIVE', 'EXAMPLE_BLOCK_PRESENT'] warnings=['NO_TOOLS_SECTION']

--- BRANCH (lane/dae2-catalog-amplifier-tester) ---
agents discovered: 2
structural summary: {'total': 2, 'passed': 2, 'errors': 0, 'warnings': 2}
quality_level: needs_work
  setup-digital-twin  chars= 595 examples=0 errors=[] warnings=['NO_TOOLS_SECTION']
  validator           chars= 592 examples=0 errors=[] warnings=['NO_TOOLS_SECTION']
```

### 5b. Full recipe on the branch — verdict quoted

Full run including its three LLM phases, on the branch. Report captured verbatim at
`evidence/validate-agents-after-full-report.md`:

> - **Overall Verdict**: ⚠️ **PASS WITH WARNINGS**
> - **Agents Found**: 2 total across 1 location
> - **Quality Breakdown**: 0 good, 0 polish, **2 needs_work**, 0 critical
> - **Issues**: **0 errors**, **2 warnings**, 0 suggestions

Coverage block, verbatim from the run's own `discovery_results`:

```
Candidates: 2 files matched the scan
Classified as agents: 2 across 1 locations
Classified as NON-agents: 0 ({})
Classifier: frontmatter declares a top-level `meta:` key (docs/AGENT_AUTHORING.md)
```

**Stated as fail-before / pass-after, not as a held PASS:** stock is `critical` with 4 errors; the
branch is 0 errors. `needs_work` is driven **entirely** by `NO_TOOLS_SECTION` — see §7.

**One honest caveat about the LLM phase.** The generated report asserts *"both agents were already
at the standard before this lane touched anything"* and *"the description sweep for this repo is a
no-op by design"*. That is **wrong**, and it is wrong for a structural reason worth naming: the
recipe validates only the tree it is pointed at, so the LLM phase saw the post-edit branch and
inferred a history it could not observe. §5a is the counter-evidence — the same recipe, on stock,
returns `critical` with `EXAMPLE_BLOCK_PRESENT` and `DESCRIPTION_EXCESSIVE` on both agents. The
report is published unedited, with this note beside it, rather than quietly trimmed.

---

## 6. Tests and CI

**This repo HAS CI** — `.github/workflows/ci.yml` (added on `main` @ `3ffbcd4`): `lint` (ruff
0.16.6 pinned, `--isolated --select E4,E7,E9,F`), `test` (matrix 3.11 / 3.13), and
`bundle-structure` (YAML parse gate). No path filters, no swallowed exit codes.

| | result |
|---|---|
| `python3 -m pytest tests/ -q` on stock | 18 passed |
| same, on the branch | **27 passed** |
| delta | **+9 — exactly the new guard's 9 cases, zero regressions** |
| `uvx ruff@0.16.6 check --isolated --select E4,E7,E9,F .` | **All checks passed!** |
| CI-exact test command (`uv run --isolated --no-project --python 3.13 --with pytest==9.1.1 --with PyYAML==6.0.2`) | **27 passed** |

### New repo-wide guard: `tests/test_agent_description_policy.py`

Walks `agents/*.md` **as a set**, so an agent added later is covered the day it lands — a per-file
test can only guard what existed when it was written, which is how both descriptions drifted past
the policy unnoticed. Carries an empty-glob tripwire (`test_the_sweep_is_not_vacuous`), so a
directory rename breaks the guard loudly instead of silently disarming it.

Asserts, per agent: description length within `[100, 600]` (the floor is `validate-agents`' own
`MIN_DESCRIPTION_LENGTH`, so a description cannot be "shortened" into uselessness to satisfy the
ceiling); opens with `USE WHEN`; carries `DO NOT USE WHEN`; zero `<example>`/`<commentary>` markup.

**Proven red before green** (`evidence/guard-fail-before.txt`) — the guard, unchanged, run against
the stock tree:

```
8 failed, 1 passed in 0.03s
FAILED test_description_is_within_budget[agents/setup-digital-twin.md]
FAILED test_description_is_within_budget[agents/validator.md]
FAILED test_description_is_trigger_first[agents/setup-digital-twin.md]
FAILED test_description_is_trigger_first[agents/validator.md]
FAILED test_description_carries_both_routing_clauses[agents/setup-digital-twin.md]
FAILED test_description_carries_both_routing_clauses[agents/validator.md]
FAILED test_description_carries_no_example_markup[agents/setup-digital-twin.md]
FAILED test_description_carries_no_example_markup[agents/validator.md]
```

and `9 passed` on the branch.

**The guard caught a real defect in this lane's own first draft**, which is the argument for it
existing: the initial hard-wrap of `validator`'s description put a newline inside the phrase
`DO NOT USE WHEN`, so the clause was split in the rendered scalar. Fixed two ways — the wrapper now
protects both clause phrases, and the guard matches on whitespace-normalised text, because *where*
an author wraps a YAML literal block is a formatting choice with no meaning, and a guard that fails
on line-break position trains the next author to fight the wrapper instead of writing the clause.

**No test in this repo asserted that `<example>` blocks must be PRESENT** — checked; the failure
mode a sibling lane hit does not occur here.

### One CI change, and why it was necessary

The `test` job gains `--with PyYAML==6.0.2`. The new guard reads each agent's frontmatter, and the
job runs `--isolated --no-project` with pytest as its only dependency. The alternative — regexing a
YAML block scalar by hand inside the guard — would make the guard wrong in a way nothing else in
the repo would catch. Pinned rather than tracking the `bundle-structure` job's `PyYAML>=6.0` floor,
because a test dependency that can move under the gate is not pinned.

---

## 7. `NO_TOOLS_SECTION` — pre-existing, unchanged, deliberately not fixed here

Both agents carry a `NO_TOOLS_SECTION` **warning** on `main` and still do on this branch. It is
the sole reason `quality_level` is `needs_work` rather than `good`; **it is not a regression
introduced by this change**, and no lean row would move it.

It is real: `grep -r "tools:"` across the repo returns zero hits, and both agents are shell-driven
(`amplifier-digital-twin exec …`). But the correct fix is a `tools:` block in
`behaviors/amplifier-tester.yaml`, and that **contradicts the README's stated contract** — *"This
bundle doesn't ship a runtime (no provider, orchestrator, or tools) — it must be composed onto a
bundle that does."* Whether the resolver dedupes by module id or double-registers when composed
onto a host that already declares `tool-bash` is **unverified**, and verifying it needs a DTU run
this lane has no authority to fund. Adding `tools:` to either agent's frontmatter would also break
this lane's byte-identical-body requirement.

Filed as a §9 open item, not fixed here.

---

## 8. Spend

Authority: **$0.00** (0 runs × 0 arms). Nothing measured against a provider API.

| Activity | API spend |
|---|---|
| Description edits, guard, CI line | $0.00 |
| Byte counts, md5s, fidelity enumeration | $0.00 |
| `validate-agents` deterministic phases 0–3, ×2 trees | $0.00 — pure bash/python |
| Local pytest ×3, ruff ×1 | $0.00 |
| `validate-agents` **full recipe** on the branch, 3 LLM steps | **not $0.00 — see below** |
| API measurement runs | **none** — not authorised, not performed |
| DTU / container infrastructure | **none created**, nothing to tear down |

**The recipe runner records no token usage.** `steps.jsonl` for the run carries **0** lines with a
`usage` object across all 12 steps, so there is no measured figure to quote and this lane will not
invent one. What can be stated exactly: **3 LLM steps** over **2 agents**, producing an 8,674-char
report. Order of magnitude: well under $1.

Two things follow, both reported rather than absorbed, and both already reported by the `kp79`
lane — they have not been fixed in the interim:

1. **Goal-text inconsistency.** "$0" and "a recipe run" cannot both be literally true while a
   *required deliverable* runs LLM steps. Either the cap should read "$0 API measurement; recipe
   runs excluded", or the deliverable should specify the deterministic phases only.
2. **Instrument gap.** A program that gates every lane on spend runs recipes through a runner that
   records no usage. Every recipe-running lane is reporting an estimate.

The cap did **not** bind. Nothing was recorded NOT-POSSIBLE.

---

## 9. CENSUS SAFETY check — CLEAN

`GOAL.md`'s pre-finish check, run verbatim:

```
grep -l /tmp/ <uv-tool-root>/lib/python3.13/site-packages/*.pth
→ (no output, exit 1)
```

**No `.pth` file references `/tmp/`.** All 60-odd editable installs point at `~/.amplifier/cache/…`
as expected. No scratch-`AMPLIFIER_HOME` `amplifier` run was performed by this lane — see §2 for
the measurement method used instead.

---

## 10. Deliverable status

| Deliverable | Status |
|---|---|
| Both descriptions trigger-first, ≤600, USE WHEN / DO NOT USE WHEN, zero example blocks | **DONE** — 595 and 592; §2 |
| FIDELITY TABLE, incl. example-only facts | **DONE** — §3. Zero protected facts lost; 5 rescued; 2 non-protected absences named with restoration cost |
| Bodies byte-identical, md5 quoted both sides | **DONE** — §4 |
| Before/after char counts per agent + repo total, vs CURRENT `origin/main` | **DONE** — §1, §2. Baseline re-derived; census was 74 chars high |
| `validate-agents` on the branch, verdict quoted, agent count quoted | **DONE** — §5. `critical` (4 errors) → **PASS WITH WARNINGS** (0 errors); 2 agents across 1 location |
| CI green where the repo has CI | **DONE** — repo has CI; §6. Local reproduction of all three jobs green |
| Anything already compliant, left unedited and named | **N/A** — both agents were out of policy on all four counts; nothing in scope was already compliant. No other file registers a catalog row |
| DRAFT PR, not merged | **DONE** — see `DONE.json` |

**Outcome branch A (RESOLVED at the draft PR).** No deliverable was NOT-POSSIBLE.

---

## 11. What remains open

1. **The merge.** The PR is draft by design — the manager merges (LANDING STAGE).
2. **`NO_TOOLS_SECTION` on both agents** (§7) — real, pre-existing, needs a DTU-verified answer on
   resolver dedupe before the behavior-level `tools:` block can land. Wants its own item.
3. **`GOAL.md` names the shared parent item** (§0) rather than a per-repo child. Fix before the
   next batch.
4. **The recipe runner records no token usage** (§8) — every spend-gated lane that runs a recipe is
   reporting an estimate.
5. **The census figure for this repo was 74 chars high** (§1). Minor, but it is the second lane in
   this sweep to find its baseline drifted; treat every remaining repo's census number as an
   estimate to verify, not a measurement.
