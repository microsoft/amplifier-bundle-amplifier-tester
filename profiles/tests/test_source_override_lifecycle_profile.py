"""
Tests for amplifier-source-override-lifecycle.yaml profile.

Validates that the DTU profile exists, has valid YAML structure, and covers
the expected source-override scenarios (D1-D5).
"""

import os
import yaml
import pytest

PROFILE_PATH = os.path.join(
    os.path.dirname(__file__),
    "amplifier-source-override-lifecycle.yaml",
)


def load_profile():
    with open(PROFILE_PATH) as f:
        return yaml.safe_load(f)


# ── existence ────────────────────────────────────────────────────────────────

def test_profile_file_exists():
    """Profile YAML file must exist on disk."""
    assert os.path.exists(PROFILE_PATH), (
        f"Profile file not found: {PROFILE_PATH}"
    )


# ── top-level structure ───────────────────────────────────────────────────────

def test_profile_has_required_top_level_keys():
    """Profile must have name, description, base, passthrough, provision, update, readiness."""
    profile = load_profile()
    for key in ("name", "description", "base", "passthrough", "provision", "update", "readiness"):
        assert key in profile, f"Missing top-level key: {key!r}"


def test_profile_name():
    """name field must match the expected profile identifier."""
    profile = load_profile()
    assert profile["name"] == "amplifier-source-override-lifecycle"


def test_profile_base_image():
    """base.image must be ubuntu:24.04 (consistent with Profile 1)."""
    profile = load_profile()
    assert profile["base"]["image"] == "ubuntu:24.04"


# ── passthrough ───────────────────────────────────────────────────────────────

def test_passthrough_forwards_anthropic_key():
    """passthrough must forward the Anthropic API key (same as Profile 1)."""
    profile = load_profile()
    services = profile["passthrough"]["services"]
    names = [s["name"] for s in services]
    assert "anthropic" in names, "passthrough.services must include anthropic service"
    anthropic_svc = next(s for s in services if s["name"] == "anthropic")
    assert anthropic_svc.get("key_env") == "ANTHROPIC_API_KEY"


# ── provision section ─────────────────────────────────────────────────────────

def _provision_cmds_text(profile):
    """Return all provision setup_cmds joined as a single string for scanning."""
    cmds = profile["provision"].get("setup_cmds", [])
    return "\n".join(str(c) for c in cmds)


def test_provision_installs_uv():
    """Provision must install uv."""
    profile = load_profile()
    text = _provision_cmds_text(profile)
    assert "astral.sh/uv/install.sh" in text, "provision must install uv"


def test_provision_installs_amplifier_from_git():
    """Provision must install Amplifier CLI via uv tool install from git."""
    profile = load_profile()
    text = _provision_cmds_text(profile)
    assert "uv tool install git+" in text and "amplifier" in text, (
        "provision must install Amplifier via uv tool install git+"
    )


def test_provision_writes_settings_yaml():
    """Provision must write settings.yaml with Anthropic provider config."""
    profile = load_profile()
    text = _provision_cmds_text(profile)
    assert "settings.yaml" in text
    assert "provider-anthropic" in text


def test_provision_d1_clones_local_repo():
    """D1 scenario: provision must git clone the anthropic provider module locally."""
    profile = load_profile()
    text = _provision_cmds_text(profile)
    assert "git clone" in text
    assert "amplifier-module-provider-anthropic" in text
    assert "/root/dev" in text, "local clone should go under /root/dev"


def test_provision_d1_runs_source_add():
    """D1 scenario: provision must call 'amplifier source add provider-anthropic' with local path."""
    profile = load_profile()
    text = _provision_cmds_text(profile)
    assert "amplifier source add" in text
    assert "provider-anthropic" in text
    assert "--global" in text


def test_provision_override_active_check():
    """D1 scenario: provision must verify override is active via 'amplifier source show'."""
    profile = load_profile()
    text = _provision_cmds_text(profile)
    assert "amplifier source show" in text
    assert "OVERRIDE_ACTIVE" in text


def test_provision_override_importable_check():
    """D1 scenario: provision must verify the overridden module is importable from local path."""
    profile = load_profile()
    text = _provision_cmds_text(profile)
    assert "OVERRIDE_IMPORTABLE" in text
    assert "amplifier_module_provider_anthropic" in text


def test_provision_pth_snapshot():
    """Provision must save a .pth snapshot for comparison in update section."""
    profile = load_profile()
    text = _provision_cmds_text(profile)
    assert "snapshot" in text.lower()
    assert "pth" in text.lower()


# ── update section ────────────────────────────────────────────────────────────

def _update_cmds_text(profile):
    """Return all update cmds joined as a single string for scanning."""
    cmds = profile["update"].get("cmds", [])
    return "\n".join(str(c) for c in cmds)


def test_update_runs_amplifier_update():
    """D2 scenario: update section must run 'amplifier update --yes'."""
    profile = load_profile()
    text = _update_cmds_text(profile)
    assert "amplifier update --yes" in text


def test_update_d2_override_still_active():
    """D2 scenario: after update, local override must still be active (OVERRIDE_ACTIVE)."""
    profile = load_profile()
    text = _update_cmds_text(profile)
    assert "OVERRIDE_ACTIVE" in text


def test_update_d2_pth_points_to_override():
    """D2 scenario: after update, .pth must still point to local path (PTH_POINTS_TO_OVERRIDE)."""
    profile = load_profile()
    text = _update_cmds_text(profile)
    assert "PTH_POINTS_TO_OVERRIDE" in text


def test_update_pth_integrity_check():
    """Update section must verify PTH_INTEGRITY for all providers after update."""
    profile = load_profile()
    text = _update_cmds_text(profile)
    assert "PTH_INTEGRITY" in text


def test_update_session_viable_check():
    """Update section must verify a full session completes (SESSION_VIABLE)."""
    profile = load_profile()
    text = _update_cmds_text(profile)
    assert "SESSION_VIABLE" in text or "amplifier run" in text


def test_update_d5_documented_as_comment():
    """D5 scenario: must be documented (comment noting same code path as U4/Profile 1)."""
    with open(PROFILE_PATH) as f:
        raw = f.read()
    assert "D5" in raw, "D5 scenario should be referenced in the profile"


# ── readiness ─────────────────────────────────────────────────────────────────

def test_readiness_amplifier_installed():
    """readiness must include an amplifier --version check."""
    profile = load_profile()
    readiness = profile["readiness"]
    assert any(
        "amplifier --version" in str(r.get("command", "")) or
        r.get("name") == "amplifier-installed"
        for r in readiness
    ), "readiness must have amplifier-installed check"
