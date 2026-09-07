# Fidelity table — re-verified at today's head, not inherited

Target: `context/amplifier-tester-awareness.md`
Stock at `7b37ad0` (today's head of `main` when this lane started): **2,068 chars**
Lean (V1 span 2 body): **1,242 chars**
Saved: **826 chars**

`zc6t` recorded this target as CLEAN (`fidelity-report.json`, index 2,
`missing_rules: []`). That table was **not inherited**. Every row below was
re-derived by reading both texts at today's head. Result: **no rule, constraint,
command or pointer present in stock is absent from lean.**

## Precondition checked first

The stock file in this repo at `7b37ad0` is **byte-identical** to the copy
`zc6t` resolved and measured
(`~/.amplifier/cache/amplifier-bundle-amplifier-tester-51fb043af4f8b374/context/amplifier-tester-awareness.md`),
`diff` clean, both 2,068 chars. So the patch was authored against exactly the
text it was applied to — no drift in between. It applied with `git apply`, which
does no fuzzy placement at all: **zero hunks relocated, zero fuzz, no hand-port
needed.**

## Row-by-row

| # | Rule / constraint / command / pointer in STOCK | In LEAN? | How it reads in lean |
|---|---|---|---|
| 1 | Purpose: tests changes to Amplifier repos in isolated DTU environments | YES | "Tests changes to Amplifier repos … in isolated DTUs" |
| 2 | Scope list: core, modules, bundles, foundation, app-cli | YES | verbatim |
| 3 | Use case: local ecosystem changes need validating | YES | "local ecosystem changes" |
| 4 | Use case: bundle/module/prompt changes before pushing to GitHub | YES | verbatim phrase retained |
| 5 | Use case: multi-repo changes verified together in isolation | YES | "multi-repo changes verified together" |
| 6 | **Do NOT** use for apps/things outside the Amplifier ecosystem | YES | "Do NOT use it for apps or anything outside the Amplifier ecosystem" |
| 7 | Pointer: use `amplifier-bundle-reality-check` instead | YES | verbatim, still backticked |
| 8 | If not installed, tell the user to get that bundle | YES | verbatim |
| 9 | Only use this bundle if they insist | YES | "use this one only if they insist" |
| 10 | Command: `delegate(agent="amplifier-tester:setup-digital-twin", …)` | YES | **verbatim, character for character** |
| 11 | Command: `delegate(agent="amplifier-tester:validator", …)` | YES | **verbatim, character for character** |
| 12 | Resource accounting is the **orchestrator's** responsibility | YES | "Resource accounting is yours" |
| 13 | Repeated delegations **accumulate** environments; each launches its own DTU | YES | "every `setup-digital-twin` launches another DTU" |
| 14 | May create or reuse a Gitea instance | YES | "(may create/reuse Gitea)" |
| 15 | Nothing tears them down automatically | YES | "nothing is torn down automatically" |
| 16 | The sub-agent is **stateless** — cannot see siblings or live environments | YES | "the sub-agent is stateless — blind to siblings and live environments" |
| 17 | Track how many DTUs launched **across all delegations** | YES | "Track DTUs launched across all delegations" |
| 18 | Set and enforce a **hard cap** on concurrent environments | YES | "enforce a hard cap on concurrent environments" |
| 19 | Pass the **current live count and remaining budget** in every `setup-digital-twin` delegation | YES | "pass the current live count plus remaining budget in every `setup-digital-twin` instruction" |
| 20 | N delegations silently launch N environments; can exhaust host disk | YES | verbatim in substance |

**Missing: none. Restored: nothing needed restoring.**

## What was compressed but NOT lost — stated so the compression is auditable

Three things changed shape without changing what the reader is told to do:

1. **Section headings dropped** (`## When to Use`, `## How to Use`,
   `## ⚠️ Resource Accounting (orchestrator responsibility)`). The
   orchestrator-responsibility framing survives as the sentence
   "Resource accounting is yours"; the ⚠️ glyph is gone.
2. **One rationale clause dropped**, not a rule: stock says pass the count
   "*so the sub-agent can confirm scope before adding another*". The
   instruction (pass live count + remaining budget, every time) is intact; only
   the explanation of why is gone.
3. **Bullet lists folded into prose.** No list item lost a member — rows 3–5
   and 17–19 above are the same items, run together.

Row 2 of the item's warning — *"the required-rules check must pin it, not just
the agent names"* — is why the guardrail's
`REQUIRED_RULES["resource accounting (orchestrator responsibility)"]` carries
twelve separate assertions covering rows 12–20, not one assertion on
`amplifier-tester:setup-digital-twin`.

## Honest limit of the mechanical check

`zc6t`'s `fidelity_diff.py` extractor, re-run here against today's stock,
extracts exactly **two** tokens: `` `amplifier-bundle-reality-check` `` and
`` `setup-digital-twin` ``. Both survive. But two tokens is not coverage of a
2,068-char file — the stock text states its rules in prose and fenced blocks
rather than in inline code spans and ALL-CAPS imperatives, which is what that
extractor looks for. **The CLEAN verdict in `zc6t`'s report for this target is
therefore weakly evidenced by the extractor alone**, and the table above — read
by hand, row by row — is the actual evidence. The guardrail pins both layers,
and `test_the_extractor_is_known_to_be_thin_here` pins the limitation itself so
nobody mistakes layer 1 for coverage.
