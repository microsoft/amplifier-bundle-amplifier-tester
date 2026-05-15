#!/usr/bin/env bash
# Runs INSIDE the outer DTU. Performs all checks against the inner DTU
# launched by the setup-digital-twin agent and emits a JSON report to
# stdout.
#
# Usage (inside outer DTU):
#   ./inner-checks.sh > /root/checks.json
#
# The script never aborts on a failed check — each criterion is recorded
# independently in the JSON output.

set -uo pipefail
export PATH="/root/.local/bin:$PATH"

# Inner exec'd commands use --stream so stdout is the raw command output, not
# the default JSON envelope. --timeout none disables the 600s default cap so
# the smoke `amplifier run` (which is slow) doesn't get killed.

# ----- locate the generated profile YAML --------------------------------------
PROFILE_PATH=""
for cand in /tmp/amplifier-tester/profile-*.yaml \
            /root/.amplifier/digital-twin-universe/profiles/*.yaml \
            /root/profiles/*.yaml; do
  if [ -f "$cand" ]; then
    PROFILE_PATH="$cand"
    break
  fi
done
if [ -n "$PROFILE_PATH" ]; then
  PROFILE_GENERATED="true"
else
  PROFILE_GENERATED="false"
fi

# ----- list inner DTUs --------------------------------------------------------
INNER_LIST_RAW="$(amplifier-digital-twin list 2>/dev/null || echo '[]')"
INNER_ID="$(echo "$INNER_LIST_RAW" | jq -r '.[0].id // empty' 2>/dev/null || true)"
INNER_STATUS="$(echo "$INNER_LIST_RAW" | jq -r '.[0].status // empty' 2>/dev/null || true)"

# Engine returns "Running" (capital R) — match case-insensitively.
INNER_STATUS_LOWER="$(echo "${INNER_STATUS:-}" | tr '[:upper:]' '[:lower:]')"
if [ "$INNER_STATUS_LOWER" = "running" ]; then
  INNER_DTU_RUNNING="true"
else
  INNER_DTU_RUNNING="false"
fi

# ----- amplifier --version inside the inner DTU -------------------------------
AMPLIFIER_VERSION_OUTPUT=""
AMPLIFIER_VERSION_OK="false"
if [ -n "$INNER_ID" ]; then
  AMPLIFIER_VERSION_OUTPUT="$(amplifier-digital-twin exec --stream "$INNER_ID" -- bash -c 'PATH=/root/.local/bin:$PATH amplifier --version' 2>&1 | head -c 4000 || true)"
  if echo "$AMPLIFIER_VERSION_OUTPUT" | grep -qiE '^amplifier,? +version'; then
    AMPLIFIER_VERSION_OK="true"
  fi
fi

# ----- bundle list inside the inner DTU ---------------------------------------
BUNDLE_LIST_OUTPUT=""
BUILD_UP_FOUNDATION_PRESENT="false"
if [ -n "$INNER_ID" ]; then
  BUNDLE_LIST_OUTPUT="$(amplifier-digital-twin exec --stream "$INNER_ID" -- bash -c 'PATH=/root/.local/bin:$PATH amplifier bundle list' 2>&1 | head -c 8000 || true)"
  if echo "$BUNDLE_LIST_OUTPUT" | grep -q 'build-up-foundation'; then
    BUILD_UP_FOUNDATION_PRESENT="true"
  fi
fi

# ----- smoke run inside the inner DTU -----------------------------------------
# Always attempt the smoke run if an inner DTU exists, even if the version
# probe failed — version probe failure does not imply the smoke run will fail.
SMOKE_OUTPUT=""
SMOKE_OK="false"
if [ -n "$INNER_ID" ]; then
  SMOKE_OUTPUT="$(amplifier-digital-twin exec --stream --timeout none "$INNER_ID" -- bash -c 'PATH=/root/.local/bin:$PATH amplifier run --mode single "Say exactly: build-up-foundation-ok"' 2>&1 | head -c 32000 || true)"
  if echo "$SMOKE_OUTPUT" | grep -q 'build-up-foundation-ok'; then
    SMOKE_OK="true"
  fi
fi

# ----- emit JSON ---------------------------------------------------------------
jq -n \
  --arg profile_path "${PROFILE_PATH}" \
  --argjson profile_generated "${PROFILE_GENERATED}" \
  --arg inner_id "${INNER_ID}" \
  --arg inner_status "${INNER_STATUS}" \
  --argjson inner_dtu_running "${INNER_DTU_RUNNING}" \
  --arg amplifier_version_output "${AMPLIFIER_VERSION_OUTPUT}" \
  --argjson amplifier_version_ok "${AMPLIFIER_VERSION_OK}" \
  --arg bundle_list_output "${BUNDLE_LIST_OUTPUT}" \
  --argjson build_up_foundation_present "${BUILD_UP_FOUNDATION_PRESENT}" \
  --arg smoke_output "${SMOKE_OUTPUT}" \
  --argjson smoke_ok "${SMOKE_OK}" \
  '{
    profile_path: $profile_path,
    profile_generated: $profile_generated,
    inner_id: $inner_id,
    inner_status: $inner_status,
    inner_dtu_running: $inner_dtu_running,
    amplifier_version_output: $amplifier_version_output,
    amplifier_version_ok: $amplifier_version_ok,
    bundle_list_output: $bundle_list_output,
    build_up_foundation_present: $build_up_foundation_present,
    smoke_output: $smoke_output,
    smoke_ok: $smoke_ok
  }'
