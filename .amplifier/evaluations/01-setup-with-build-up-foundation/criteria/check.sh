#!/usr/bin/env bash
# Drives the 6 success criteria for evaluation 01.
#
# Usage:
#   check.sh <OUTER_DTU_ID> <RESULTS_DIR> <STDOUT_PATH>
#
# Steps:
#   1. Push criteria/inner-checks.sh into the outer DTU.
#   2. Exec it to perform criteria 1-5 against the inner DTU; capture JSON.
#   3. Score criterion 6 (handback) against the captured stdout on the host.
#   4. Emit results/criteria.txt (human-readable) and results/metrics.json.
#   5. Exit 0 if all 6 pass, non-zero otherwise.

set -uo pipefail

OUTER_ID="${1:?Usage: check.sh OUTER_ID RESULTS_DIR STDOUT_PATH}"
RESULTS="${2:?Usage: check.sh OUTER_ID RESULTS_DIR STDOUT_PATH}"
STDOUT_PATH="${3:?Usage: check.sh OUTER_ID RESULTS_DIR STDOUT_PATH}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

mkdir -p "$RESULTS"

# ----- push & run inner-checks.sh inside the outer DTU ------------------------
echo "[check] pushing inner-checks.sh into outer DTU $OUTER_ID" >&2
amplifier-digital-twin file-push "$OUTER_ID" "$SCRIPT_DIR/inner-checks.sh" /root/inner-checks.sh >/dev/null

echo "[check] executing inner checks (may take several minutes for smoke run)" >&2
# --stream so inner-checks.json receives the RAW JSON written by inner-checks.sh,
# not the default JSON envelope from amplifier-digital-twin exec.
# --timeout none disables the 600s default cap; the smoke run is slow.
amplifier-digital-twin exec --stream --timeout none "$OUTER_ID" -- bash -c \
  'chmod +x /root/inner-checks.sh && /root/inner-checks.sh' \
  > "$RESULTS/inner-checks.json" 2> "$RESULTS/inner-checks.stderr"

# ----- score handback (criterion 6) against captured stdout -------------------
HANDBACK_PARTS=0
if [ -f "$STDOUT_PATH" ]; then
  # Extract the inner DTU id from the JSON for grep targeting.
  INNER_ID_FOR_GREP="$(jq -r '.inner_id // ""' "$RESULTS/inner-checks.json" 2>/dev/null || true)"
  if [ -n "$INNER_ID_FOR_GREP" ] && grep -q -- "$INNER_ID_FOR_GREP" "$STDOUT_PATH"; then
    HANDBACK_INSTANCE_ID="true"; HANDBACK_PARTS=$((HANDBACK_PARTS+1))
  else
    HANDBACK_INSTANCE_ID="false"
  fi
  if grep -qE "amplifier-digital-twin[[:space:]]+exec" "$STDOUT_PATH"; then
    HANDBACK_EXEC="true"; HANDBACK_PARTS=$((HANDBACK_PARTS+1))
  else
    HANDBACK_EXEC="false"
  fi
  if grep -qE "amplifier-digital-twin[[:space:]]+destroy" "$STDOUT_PATH"; then
    HANDBACK_DESTROY="true"; HANDBACK_PARTS=$((HANDBACK_PARTS+1))
  else
    HANDBACK_DESTROY="false"
  fi
  # The profile path is sometimes mentioned, sometimes embedded in a
  # destroy/exec example. Accept either an explicit "/tmp/amplifier-tester/"
  # path mention or a literal "profile" word near a yaml extension.
  if grep -qE '(/tmp/amplifier-tester/profile|\.amplifier/digital-twin-universe/profiles|profile-[0-9].*\.yaml)' "$STDOUT_PATH"; then
    HANDBACK_PROFILE="true"; HANDBACK_PARTS=$((HANDBACK_PARTS+1))
  else
    HANDBACK_PROFILE="false"
  fi
else
  HANDBACK_INSTANCE_ID="false"
  HANDBACK_EXEC="false"
  HANDBACK_DESTROY="false"
  HANDBACK_PROFILE="false"
fi

if [ "$HANDBACK_PARTS" -ge 4 ]; then
  HANDBACK_COMPLETE="true"
else
  HANDBACK_COMPLETE="false"
fi

# ----- merge into a single metrics.json --------------------------------------
jq -s --argjson handback_parts "$HANDBACK_PARTS" \
       --arg handback_instance_id "$HANDBACK_INSTANCE_ID" \
       --arg handback_exec "$HANDBACK_EXEC" \
       --arg handback_destroy "$HANDBACK_DESTROY" \
       --arg handback_profile "$HANDBACK_PROFILE" \
       --arg handback_complete "$HANDBACK_COMPLETE" \
  '.[0] + {
     handback_parts_found: $handback_parts,
     handback_instance_id: ($handback_instance_id == "true"),
     handback_exec: ($handback_exec == "true"),
     handback_destroy: ($handback_destroy == "true"),
     handback_profile: ($handback_profile == "true"),
     handback_complete: ($handback_complete == "true")
   }' "$RESULTS/inner-checks.json" > "$RESULTS/metrics.json"

# ----- human-readable summary -------------------------------------------------
# Note: build the summary in a tmp file (not via `| tee`) so the variable
# scoping survives — `{ ... } | tee` runs the brace group in a subshell and
# loses mutations to PASS/FAIL.

M="$RESULTS/metrics.json"
TMP="$RESULTS/criteria.txt"
: > "$TMP"

PASS=0
FAIL=0
print_check() {
  local name="$1" pass="$2"
  if [ "$pass" = "true" ]; then
    echo "PASS: $name" | tee -a "$TMP"
    PASS=$((PASS+1))
  else
    echo "FAIL: $name" | tee -a "$TMP"
    FAIL=$((FAIL+1))
  fi
}

print_check "1. profile-generated"              "$(jq -r .profile_generated "$M")"
print_check "2. inner-dtu-running"              "$(jq -r .inner_dtu_running "$M")"
print_check "3. amplifier-version"              "$(jq -r .amplifier_version_ok "$M")"
print_check "4. build-up-foundation-bundle"     "$(jq -r .build_up_foundation_present "$M")"
print_check "5. inner-smoke-run"                "$(jq -r .smoke_ok "$M")"
print_check "6. handback-complete"              "$(jq -r .handback_complete "$M")"

echo                                  | tee -a "$TMP"
echo "Summary: $PASS passed, $FAIL failed" | tee -a "$TMP"

if [ "$FAIL" -eq 0 ]; then
  exit 0
else
  exit 1
fi
