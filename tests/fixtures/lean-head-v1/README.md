# lean-head-v1 fixtures — provenance

Two verbatim, hand-off-limits reference texts for
`tests/test_lean_head_guardrail.py`. Neither is a paraphrase; both are byte
copies, so the guardrail compares against what was actually measured rather
than against a description of it.

## `amplifier-tester-awareness.md` — the V1 lean text (1,242 chars)

A verbatim copy of **span 2's body** from
`probes/bji-lean-head/v1_instructions.json` in the `openai-evals-team-ci`
repo, with the `<context_file paths=...>` wrapper the shim adds stripped
(`body.split(">", 1)[1]`, trailing `</context_file>` removed, `strip("\n")`,
one trailing newline) — the same normalisation
`docs/lanes/zc6t-lean-head-ship/tools/fidelity_diff.py` applies in
`microsoft/amplifier-foundation`.

`sha256 = 1f9d7b1b6df122ecdc432129c0c55149a6ba636c804cdb8045c8e6d224f2e27a`

The identical bytes ship as
`docs/lanes/zc6t-lean-head-ship/patches/context-files/02-amplifier-bundle-amplifier-tester-amplifier-tester-awareness.md.lean.md`
on `main` of `microsoft/amplifier-foundation` (PR #372). Verified equal to the
span body at the time this fixture was vendored.

## `amplifier-tester-awareness.stock.md` — the pre-change text (2,068 chars)

A verbatim copy of `context/amplifier-tester-awareness.md` as it stood at
`7b37ad0`, the commit this change was applied on top of. It exists so the
"every rule from the stock text survives" assertion has the stock text to
extract from after the stock text is gone from the working tree.

`sha256 = b64317648adb082eb29a13d762db4d633217f8f4db6f01df325650e9372377e7`

## Why the sizes are pinned

`model_performance-g7h3` measured the lean head at **-13.57 % $/task, 95 % CI
[-22.27 %, -4.86 %]** across 98 end-to-end runs ($428.10). That result was
bought against these exact bytes. A budget set above what shipped would let the
head regrow silently up to it, which is the failure this directory exists to
prevent.
