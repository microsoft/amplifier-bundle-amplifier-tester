# Goal defect: the terminal-outcome set is unsatisfiable for a non-holding lane

**Filed under the goal's own instruction:** *"If the only way to satisfy a
deliverable is to write a file outside your worktree … that is a DEFECT IN THIS
GOAL, not a task. Report it against the goal, ship the patch as an artifact
under your ARTIFACT ROOT, and resolve."* This is that artifact. The proposed
patch is at the bottom, ready to paste into the goal template.

---

## The defect, stated once

The goal offers three terminal outcomes and calls them **exhaustive**. Every one
of them terminates in a work-tracker mutation on `model_performance-j1e6`:

| Outcome | Terminal verb |
|---|---|
| **A. RESOLVED** | `work_resolve` |
| **B. RESOLVED AT THE CAP** | `work_resolve` (branch A's verb, explicitly) |
| **C. BLOCKED** | `work_release` |

**Every one of those verbs requires this session to HOLD the item.** Measured,
not inferred — all three calls were made and all three refused:

```
work_claim(project="model_performance", item_id="model_performance-j1e6")
-> already claimed by agent-spark-1-1101253                    [refused, twice]

work_resolve(id="model_performance-j1e6", reason=<lane summary>)
-> not currently holding ... refusing to resolve an item this session did not claim

work_release(id="model_performance-j1e6")
-> not currently holding ... refusing to release an item this session did not claim
```

Holding requires `work_claim` to succeed. `work_claim` refuses because the item
is attributed to another holder **and** already reads `resolved` — a resolved
item is not in the ready queue. So:

> **The outcome set {A, B, C} is exhaustive only for a lane that can obtain
> custody. For a lane that cannot, it is EMPTY.**

## Why C is not the escape hatch it looks like

C is the branch the goal provides for *"unreachable for a reason other than the
cap — a missing prerequisite, **a refused claim**, a broken dependency."* A
refused claim is named in that list, so C is plainly the intended landing spot
for this lane.

**But C's own completion condition is `work_release`, which requires the custody
whose absence created the unreachability in the first place.** The escape hatch
presupposes the thing that was blocked. That is the lock: C is self-defeating in
exactly the case it was written for.

Procedure 5 half-sees this — *"Release while you still HOLD the item"* — but that
sentence is guidance about ordering (do not `work_block` first), not a carve-out
for a lane that never held. The gap is real and unpatched.

## Why "just reopen it" is not the fix

`work_reopen(claim=true)` would manufacture custody, after which `work_release`
would succeed. This lane deliberately did **not** do that, for three reasons,
the first of which is the goal's own text:

1. **The goal forbids it in this exact circumstance.** *"Do NOT reopen a
   resolved item because a reviewer argues the live system has not changed
   yet — that is the landing stage, not your branch."* A reviewer pressing that
   the terminal state is unsatisfied, with reopening as the tempting remedy, is
   precisely the situation that sentence anticipates.
2. **It mutates another lane's record.** The stored resolution belongs to the
   wayfinder lane. Reopening clears `closed_at`, re-lands the item on today's
   date, and moves every throughput roll-up in the program by one item.
3. **It would satisfy the appearance of the procedure, not its purpose.** The
   release leg exists to free custody a lane is holding. This lane holds
   nothing — `work_list(status="held")` returns only `2un7` and `ytja`,
   `work_stats` reports `held: 2 / held_stale: 0`, and `j1e6` reads `resolved`
   with a stale holder field. A reopen would create custody solely to hand it
   back. **Nothing is blocked behind this item.**

## The reading under which outcome A *does* hold

The OUTCOME section heads itself **"OUTCOME (checkable end state)"**, and A is
phrased as a state, in the passive: *"Work item `model_performance-j1e6` … **is
resolved** with a user-readable summary AND the deliverables below exist."* It
does not say *"you called work_resolve."*

Checked as a state, today:

| A's clause | State |
|---|---|
| item `is resolved` | **true** — status `resolved` |
| `with a user-readable summary` | **true** — and it now carries this lane's slice, because errata travel with the resolution wherever it is shown (`corrected: true`) |
| `deliverables exist … on the module's origin` | **true** — shipped as a draft PR, marked ready, since merged: `main` @ `3ffbcd4`, four check-runs green |

**So A holds as a checkable end state, and is unreachable as a procedure.** Those
two readings of the same goal disagree, and that disagreement is the defect.
A lane cannot resolve it by choosing the convenient side; only the template can.

## Proposed patch

Add to the OUTCOME preamble, immediately after *"EXACTLY ONE of these three, and
they are exhaustive"*:

> **CUSTODY PRECONDITION.** All three outcomes end in a work-tracker mutation
> (`work_resolve` for A and B, `work_release` for C), and every one of those
> requires this session to HOLD the item. If `work_claim` is refused — the
> designed steady state on a deliberately one-item/many-lanes item — none of the
> three is reachable, **including C, whose own remedy needs the custody whose
> absence triggered it.** In that case, and only that case:
>
> 1. Complete every deliverable. A refused claim blocks bookkeeping, never work.
> 2. Record the lane's completion on the item with `work_erratum` — append-only,
>    requires no claim, never rewrites a stored resolution, and travels with the
>    item wherever its resolution is shown.
> 3. Write the marker with `outcome: "A-by-state"`, `outcome_conditions_met`
>    reflecting the state check above, and the verbatim refusals of every
>    terminal verb you attempted.
> 4. **Do NOT `work_reopen` to manufacture custody.** It clears `closed_at`,
>    moves every throughput roll-up, and mutates another lane's record to
>    satisfy a checkbox. That call belongs to the manager.
>
> This is not a fourth outcome branch. It is the custody precondition that A, B
> and C already assume and never state.

And amend **Procedure 1** from:

> If the claim is refused (held elsewhere / blocked), write BLOCKED.md, commit,
> write the completion marker, stop.

to:

> If the claim is refused, first determine WHY. If the item is held by a sibling
> lane on a deliberately multi-lane item, that is the designed steady state:
> read the spec with `work_list(item_id=…)` (authoritative, no claim, no
> custody), do the work, and record completion by `work_erratum` under the
> custody precondition above. Write BLOCKED.md and stop only when the refusal
> reflects a genuine prerequisite failure — not merely the absence of custody
> you were never going to get.

## Cost of not patching it

Every CI lane on this item hit this wall. Obeyed literally, Procedure 1 turns a
19-repo owner directive into 19 `BLOCKED.md` files and zero CI. What actually
happened instead is that lane after lane deviated, each one independently, each
one filing the same finding — which is a template defect reproducing itself, not
nineteen separate judgment calls.
