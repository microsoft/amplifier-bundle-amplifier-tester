#!/usr/bin/env bash
# Runner for evaluation 01-setup-with-build-up-foundation.
#
# Orchestrates the DTU-in-DTU lifecycle:
#   1. Preflight: verify host CLIs and ANTHROPIC_API_KEY.
#   2. Launch outer DTU from profiles/outer-dtu.yaml.
#   3. Push the verbatim scenario prompt into the outer DTU.
#   4. Run an Amplifier session inside the outer DTU with the prompt.
#      The session delegates to amplifier-tester:setup-digital-twin which
#      generates a profile and launches an INNER DTU.
#   5. Pull session directory + run criteria/check.sh.
#   6. Write meta.json, verdict.md.
#   7. Leave outer DTU running (user destroys manually).
#
# Optional env vars:
#   AMPLIFIER_EVAL_KEEP_OUTER  - "true" leaves the outer DTU running so you
#                                can inspect state; "false" (default)
#                                destroys it at the end. Destroying the
#                                outer DTU implicitly destroys the inner
#                                DTU (it lives inside).
#   AMPLIFIER_EVAL_RUN_NAME    - override the run directory name.

set -uo pipefail

# ----- helpers ----------------------------------------------------------------
EXAMPLE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

log()  { echo "[$(date -u +%H:%M:%S)] $*" >&2; }
die()  { log "ERROR: $*"; exit 1; }

# ----- preflight --------------------------------------------------------------
log "Preflight"
command -v amplifier-digital-twin >/dev/null || die "amplifier-digital-twin not on PATH"
command -v jq                     >/dev/null || die "jq not on PATH"
command -v incus                  >/dev/null || die "incus not on PATH (host DTU provisioning needs it)"
[ -n "${ANTHROPIC_API_KEY:-}" ]              || die "ANTHROPIC_API_KEY not set"

# ----- compute results dir ----------------------------------------------------
DATE="$(date -u +%Y-%m-%d)"
RUN_NUM=1
while [ -d "$EXAMPLE_DIR/results/$DATE/run-$RUN_NUM" ]; do
  RUN_NUM=$((RUN_NUM+1))
done
RESULTS="${AMPLIFIER_EVAL_RUN_NAME:-$EXAMPLE_DIR/results/$DATE/run-$RUN_NUM}"
mkdir -p "$RESULTS"
log "Results dir: $RESULTS"

START_EPOCH=$(date -u +%s)

# ----- launch outer DTU -------------------------------------------------------
log "Launching outer DTU (this typically takes 5-10 minutes)..."
OUTER_LAUNCH_OUT="$RESULTS/outer-dtu-launch.json"
if ! amplifier-digital-twin launch "$EXAMPLE_DIR/profiles/outer-dtu.yaml" \
       > "$OUTER_LAUNCH_OUT" 2> "$RESULTS/outer-dtu-launch.stderr"; then
  log "outer DTU launch failed; see $RESULTS/outer-dtu-launch.stderr"
  cat "$RESULTS/outer-dtu-launch.stderr" >&2 || true
  exit 1
fi
OUTER_ID="$(jq -r '.id // .instance_id // empty' "$OUTER_LAUNCH_OUT")"
if [ -z "$OUTER_ID" ]; then
  log "could not extract outer DTU id from launch output"
  cat "$OUTER_LAUNCH_OUT" >&2 || true
  exit 1
fi
log "Outer DTU launched: $OUTER_ID"

cleanup_outer() {
  # Default: destroy the outer DTU (which also destroys the nested inner DTU).
  # Set AMPLIFIER_EVAL_KEEP_OUTER=true to retain the DTU for inspection.
  if [ "${AMPLIFIER_EVAL_KEEP_OUTER:-false}" = "true" ]; then
    log "Leaving outer DTU $OUTER_ID running (AMPLIFIER_EVAL_KEEP_OUTER=true)."
    log "  enter:   amplifier-digital-twin exec $OUTER_ID"
    log "  destroy: amplifier-digital-twin destroy $OUTER_ID"
  else
    log "Destroying outer DTU $OUTER_ID (nested inner DTU goes with it)"
    amplifier-digital-twin destroy "$OUTER_ID" >/dev/null 2>&1 || \
      log "  destroy returned non-zero (may already be gone)"
  fi
}
# Note: we intentionally do NOT trap EXIT to destroy on error -- leaving the
# outer DTU around so you can inspect failures is more useful for an eval.

# ----- push scenario.md into outer DTU ----------------------------------------
log "Pushing scenario.md into outer DTU"
amplifier-digital-twin file-push "$OUTER_ID" \
  "$EXAMPLE_DIR/scenario.md" /root/scenario.md >/dev/null || \
    die "scenario.md push failed"

# ----- run the eval prompt inside the outer DTU -------------------------------
log "Running Amplifier session inside outer DTU (typically 10-25 minutes)..."
log "  This delegates to amplifier-tester:setup-digital-twin which mirrors"
log "  repos, generates a profile, and launches an inner DTU."

# We use a heredoc shell wrapper inside the outer DTU so we can:
#   - export PATH/ANTHROPIC_API_KEY explicitly
#   - run amplifier with the prompt
#   - capture the session id from amplifier output
INNER_RUN_CMD='set -uo pipefail
export PATH="/root/.local/bin:$PATH"
PROMPT="$(cat /root/scenario.md)"
echo "=== PROMPT ==="
echo "$PROMPT"
echo "=== AMPLIFIER RUN ==="
amplifier run --mode single "$PROMPT" 2>&1
echo "=== AMPLIFIER RUN END ==="'

# Use --stream so stdout.txt receives the raw session output (not the default
# JSON envelope). --timeout none avoids the 600s default cap which is too
# short for the setup-digital-twin agent's full mirror+launch+verify flow.
amplifier-digital-twin exec --stream --timeout none "$OUTER_ID" -- \
  bash -c "$INNER_RUN_CMD" \
  > "$RESULTS/stdout.txt" 2> "$RESULTS/stderr.txt"
AMPLIFIER_EXIT=$?
log "Amplifier session exit code: $AMPLIFIER_EXIT"

# ----- pull session directory out of outer DTU --------------------------------
log "Pulling session artifacts from outer DTU"
mkdir -p "$RESULTS/sessions"
amplifier-digital-twin file-pull -r "$OUTER_ID" \
  /root/.amplifier/projects "$RESULTS/sessions/" \
  >/dev/null 2>&1 || log "  (no session dir to pull; may not exist yet)"

# ----- extract the agent's final user-facing message --------------------------
# The last assistant message in the root session's transcript.jsonl is the
# agent's hand-back — a high-signal summary of what was accomplished. Save it
# as agent-final-message.md so it can be embedded into the final report.
log "Extracting agent's final message"
python3 "$EXAMPLE_DIR/metrics/extract_final_message.py" "$RESULTS" \
  > /dev/null 2>&1 || log "  (final message extraction failed; continuing)"

# ----- inner-dtu-list snapshot (for diagnostics) ------------------------------
amplifier-digital-twin exec "$OUTER_ID" -- bash -c \
  'PATH=/root/.local/bin:$PATH amplifier-digital-twin list' \
  > "$RESULTS/inner-dtu-list.json" 2>/dev/null || \
    echo "[]" > "$RESULTS/inner-dtu-list.json"

# ----- run criteria -----------------------------------------------------------
log "Scoring criteria"
if bash "$EXAMPLE_DIR/criteria/check.sh" "$OUTER_ID" "$RESULTS" "$RESULTS/stdout.txt"; then
  VERDICT="PASS"
else
  VERDICT="FAIL"
fi

END_EPOCH=$(date -u +%s)
WALL_SECONDS=$((END_EPOCH - START_EPOCH))

# ----- meta.json --------------------------------------------------------------
INNER_ID="$(jq -r '.[0].id // empty' "$RESULTS/inner-dtu-list.json" 2>/dev/null || true)"
jq -n \
  --arg date "$DATE" \
  --argjson run "$RUN_NUM" \
  --arg outer_dtu_id "$OUTER_ID" \
  --arg inner_dtu_id "${INNER_ID:-}" \
  --argjson amplifier_exit "$AMPLIFIER_EXIT" \
  --argjson wall_seconds "$WALL_SECONDS" \
  --arg verdict "$VERDICT" \
  --arg scenario_prompt "$(cat "$EXAMPLE_DIR/scenario.md")" \
  '{
    date: $date,
    run: $run,
    outer_dtu_id: $outer_dtu_id,
    inner_dtu_id: $inner_dtu_id,
    amplifier_exit: $amplifier_exit,
    wall_seconds: $wall_seconds,
    verdict: $verdict,
    scenario_prompt: $scenario_prompt
  }' > "$RESULTS/meta.json"

# ----- verdict.md -------------------------------------------------------------
python3 "$EXAMPLE_DIR/metrics/extract_metrics.py" "$RESULTS" > "$RESULTS/verdict.md" 2>&1 || true

# ----- summary ----------------------------------------------------------------
log ""
log "==================== SUMMARY ===================="
log "Verdict:           $VERDICT"
log "Wall time:         ${WALL_SECONDS}s"
log "Outer DTU:         $OUTER_ID"
log "Inner DTU:         ${INNER_ID:-<none>}"
log "Results:           $RESULTS"
log "  criteria.txt:    $RESULTS/criteria.txt"
log "  stdout.txt:      $RESULTS/stdout.txt"
log "  metrics.json:    $RESULTS/metrics.json"
log "  verdict.md:      $RESULTS/verdict.md"
log "================================================="

cleanup_outer

if [ "$VERDICT" = "PASS" ]; then
  exit 0
else
  exit 1
fi
