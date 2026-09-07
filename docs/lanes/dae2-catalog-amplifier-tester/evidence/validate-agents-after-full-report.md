<!-- Captured verbatim from the validate-agents v1.8.0 run on branch
     lane/dae2-catalog-amplifier-tester. Absolute host paths replaced with
     <repo>; nothing else altered. -->

# Agent Validation Report

## Executive Summary

- **Overall Verdict**: ⚠️ **PASS WITH WARNINGS**
- **Repository**: `<repo>`
- **Agents Found**: 2 total across 1 location
- **Quality Breakdown**: 0 good, 0 polish, **2 needs_work**, 0 critical
- **Issues**: **0 errors**, **2 warnings**, 0 suggestions

> The `needs_work` classification is driven **entirely** by a single warning code (`NO_TOOLS_SECTION`) on both agents. Both descriptions are already fully compliant with the description standard — trigger-first, under budget, USE WHEN / DO NOT USE WHEN present with sibling routing, zero example/commentary blocks. **No description edits are warranted in this repo.**

### Coverage

```
Scanned: ['<repo>/**/agents/*.md', '<repo>/agents/*.md'], excluding ['.git', '.venv', 'docs', 'node_modules', 'test-fixtures', 'tests']
Candidates: 2 files matched the scan
Classified as agents: 2 across 1 locations
Classified as NON-agents: 0 ({})
Classifier: frontmatter declares a top-level `meta:` key (docs/AGENT_AUTHORING.md)
```

| Location | Agents |
|----------|--------|
| agents/  | 2      |

_No NON-AGENTS table: `non_agent_count` is 0 — every file that matched the scan was classified as an agent._

## Quality Classification Summary

| Agent | Quality | Triggers | No Examples | Tools | Model Role | Description |
|-------|---------|----------|-------------|-------|------------|-------------|
| setup-digital-twin | needs_work | ✅ (`DO NOT`) | ✅ | ⚠️ implicit | ✅ `[reasoning, coding, general]` | 595 chars |
| validator | needs_work | ✅ (`MUST`, `DO NOT`) | ✅ | ⚠️ implicit | ✅ `[coding, general]` | 592 chars |

Both are under the 600-char WARN threshold and carry zero `<example>`/`<commentary>` blocks (the required shape).

## Model Role Coverage

- **Model Role Coverage**: **2/2** agents declare `model_role` — full coverage.

**Model Role Distribution:**

| Role | Count |
|------|-------|
| reasoning | 1 |
| coding | 2 |
| general | 2 |

**Agents Without model_role:** None.

**Invalid/Deprecated Role Warnings:** None. `model_role_issues` is empty for both agents.

## Detailed Findings

### Errors (Must Fix) — HIGH Priority

**None.** Both agents pass structural validation with `errors: 0`. Frontmatter parses, `meta:` is present, descriptions are within budget, and no example/commentary blocks exist.

### Warnings (Should Fix) — MEDIUM Priority

```
[MEDIUM] Agent: setup-digital-twin - NO_TOOLS_SECTION
Problem: No explicit `tools:` declaration anywhere in the repo. The agent is
         ~90% shell-driven (amplifier-digital-twin launch/exec/destroy,
         amplifier-gitea, git/rsync/curl/incus/jq) plus file I/O (reads
         ~/.amplifier/settings.yaml, writes the generated profile YAML).
         tool-bash and tool-filesystem are supplied only by the host bundle.
Before:  meta: { name, description }, model_role: [...]  — no tools key;
         `grep -r "tools:"` across the repo returns zero hits.
After:   Declare once at behavior level (NOT per-agent), in
         behaviors/amplifier-tester.yaml above the existing `agents:` block:

           tools:
             - module: tool-bash
               source: git+https://github.com/microsoft/amplifier-module-tool-bash@main
             - module: tool-filesystem
               source: git+https://github.com/microsoft/amplifier-module-tool-filesystem@main
```

```
[MEDIUM] Agent: validator - NO_TOOLS_SECTION
Problem: Same root cause. Every check in the body is an
         `amplifier-digital-twin exec <id> -- ...` invocation, so tool-bash is
         load-bearing and undeclared. Filesystem access is not required by the
         body and should not be added for this agent.
Before:  no tools key
After:   Covered by the same behavior-level `tool-bash` declaration above —
         do not duplicate into agent frontmatter, which would drift.
```

**Decision required before anyone applies this fix.** The README states the contract explicitly: *"This bundle doesn't ship a runtime (no provider, orchestrator, or tools) — it must be composed onto a bundle that does."* Declaring `tool-bash`/`tool-filesystem` here contradicts that contract, and composing onto foundation (which already declares both) would re-declare them. **Whether the resolver dedupes by module id or double-registers was not verified** — it must be tested in a DTU before merge. If dedupe is not clean, the correct fix is documentation-only: state the runtime requirement in the README and accept the warning as by-design.

One partial mitigation already exists and is worth noting: `tool-skills` **is** traceably declared via the include chain (`behaviors/amplifier-tester.yaml` → `amplifier-bundle-digital-twin-universe`, which declares `tools: [tool-skills]`). So `setup-digital-twin`'s REQUIRED first step, `load_skill(skill_name="digital-twin-universe")`, is backed by a real declaration. That is not a gap.

### Suggestions (Consider) — LOW Priority

**None.** Both descriptions already satisfy every description-quality criterion:

- **setup-digital-twin** (594 chars re-measured / 595 reported) opens trigger-first with a concrete deciding factor — `USE WHEN local changes to Amplifier ecosystem repos … need testing in an isolated DTU container before merging` — and routes both negative branches to named alternates (`reality-check`, `validator`).
- **validator** (591 / 592) opens on a *state condition* — `USE WHEN a Digital Twin Universe (DTU) is already launched and needs checking, right after setup-digital-twin hands it off` — which is precisely the discriminator against its sibling, and routes both negative branches (`setup-digital-twin`, `reality-check`).

An edit to either description would exist only to produce a diff. **Leave both unedited.**

## Remediation Priority

1. **[MEDIUM] Decide the tools-declaration question — do not act on it in this lane.** The gap is real but belongs in `behaviors/amplifier-tester.yaml`, and the fix conflicts with a stated README contract that needs a DTU-verified answer on resolver dedupe behavior. Open a separate issue.
2. **[LOW] Note both `NO_TOOLS_SECTION` warnings as pre-existing and out of scope** in the PR body for this lane, so the warnings are not mistaken for regressions introduced here.
3. **No action on descriptions.** Record this repo's slice as "already compliant, left unedited."

**Scope guard:** adding a `tools:` key to either agent's frontmatter would violate this lane's byte-identical-body requirement and produce a diff unrelated to the catalog standard. The behavior-level location is both the correct fix and the one that keeps agent files untouched.

## Metadata

- **Validated**: 2026-09-07
- **Recipe**: validate-agents v1.8.0
- **Discovery scope**: repo-wide `agents/*.md`. Scan patterns: `["<repo>/**/agents/*.md", "<repo>/agents/*.md"]`. Excluded parts: `[".git", ".venv", "docs", "node_modules", "test-fixtures", "tests"]`.
- **Agents discovered**: **2 total** across the locations in `location_counts` — `agents/`: 2.
- **Classification**: `candidates_scanned`: **2**. Classifier: **frontmatter declares a top-level `meta:` key (docs/AGENT_AUTHORING.md)** (mode: `yaml`). `non_agent_count`: **0** — `non_agents_found` is empty, so there are no excluded files to enumerate.
- **Quality Thresholds**: see `foundation:context/shared/description-authoring-principles.md` (canonical — not restated here). Gates: no structural errors (including any `<example>`/`<commentary>` block in the description — rejected entirely per V3, not merely capped), explicit tools section, description ≥ 100 chars, description length cap in CHARS (v1.8.0: WARN >600, ERROR >1200 — the superseded token tier put its ERROR above the longest description in every aligned repo measured, so it could not fire). An author over the cap should use `foundation:recipes/refresh-descriptions.yaml`, which proposes a rewrite WITH a fidelity table rather than shortening by eye. MUST/ALWAYS/REQUIRED/PROACTIVELY keyword presence is reported as a metric, not a gate.
- **Severity Guide**:
  - **ERROR (critical)**: Invalid YAML, missing required fields, or any `<example>`/`<commentary>` block in the description (will break, or is rejected per V3)
  - **WARNING (needs_work)**: No explicit tools, relying on inheritance, or description over budget (may break or bloat every session)
  - **SUGGESTION (polish)**: Missing WHEN deciding factor (quality improvement)

---

**Bottom line:** 0 errors, 2 identical warnings, both on tool declarations rather than descriptions. The description sweep for this repo is a **no-op by design** — both agents were already at the standard before this lane touched anything, and saying so is the correct deliverable.
