"""Local contract guards. Not agent behavior, a Docker lifecycle or model proof.

The opt-in runner exercises the real installed boundary; these tests cheaply
prevent the known legacy/default and ownership regressions from returning.
"""

from pathlib import Path
import re
import subprocess

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
PIN = "88d9d84149eee914372c1ca8d68e9eb9f4ba3290"
PROFILE = ROOT / ".agents/digital-twin-universe/amplifier-tester-self-validation/compose.yaml"


def text(path: str) -> str:
    return (ROOT / path).read_text()


def norm(value: str) -> str:
    return re.sub(r"\s+", " ", value)


def smart_profile(value: dict) -> None:
    assert "services" in value and "x-dtu" in value
    assert not {"base", "provision", "update", "url_rewrites", "pypi_overrides", "passthrough"} & value.keys()
    assert value["x-dtu"]["twin_machine"] in value["services"]
    assert value["x-dtu"]["repositories"]


def test_default_behavior_registers_knowledge_not_raw_package_or_legacy_bundle():
    behavior = yaml.safe_load(text("behaviors/amplifier-tester.yaml"))
    assert not behavior.get("includes")
    assert not {"session", "providers", "instruction", "skills"} & behavior.keys()
    assert behavior["agents"]["include"] == ["amplifier-tester:setup-digital-twin", "amplifier-tester:validator"]
    assert len(behavior["tools"]) == 1
    tool = behavior["tools"][0]
    assert tool["module"] == "tool-skills"
    assert tool["config"]["skills"] == [
        f"git+https://github.com/microsoft/amplifier-smart-tool-digital-twin-universe@{PIN}#subdirectory=skills"
    ]
    assert "#subdirectory=modules/tool-skills" in tool["source"]


def test_namespace_anchor_preserved():
    front = yaml.safe_load(text("bundle.md").split("---")[1])
    assert front["bundle"]["name"] == "amplifier-tester"
    assert front["includes"] == [{"bundle": "amplifier-tester:behaviors/amplifier-tester"}]


def test_maintained_profile_is_compose_and_legacy_counterexample_fails_oracle():
    smart_profile(yaml.safe_load(PROFILE.read_text()))
    old = yaml.safe_load(text("tests/fixtures/legacy-incus/amplifier-tester-self-validation.yaml"))
    with pytest.raises(AssertionError):
        smart_profile(old)
    assert "ANTHROPIC_API_KEY" in str(old)  # Counterexample preserved, not sanitized to green.


def test_profile_is_credential_free_and_has_no_host_bind_or_privilege():
    profile = yaml.safe_load(PROFILE.read_text())
    service = profile["services"]["tester"]
    assert not service.get("volumes") and not service.get("privileged")
    assert not {"network_mode", "pid", "ports"} & service.keys()
    assert service["user"] == "1000:1000"
    assert service["environment"]["HOME"] == "/home/tester"
    assert service["cpus"] > 0 and service["mem_limit"] and service["pids_limit"]
    assert service["healthcheck"]["test"][0] == "CMD"
    assert "API_KEY" not in PROFILE.read_text() and "TOKEN" not in PROFILE.read_text()
    assert len(profile["x-dtu"]["repositories"]) == 4


@pytest.mark.parametrize("agent", ["setup-digital-twin", "validator"])
def test_backend_binding_negative_contracts(agent):
    body = norm(text(f"agents/{agent}.md"))
    assert "unsupported-binding: legacy Incus instance requires its original owner, endpoint, and amplifier-digital-twin interface" in body
    assert "unsupported-binding: Smart Tool CLI unavailable" in body
    assert 'load_skill(info="digital-twin-universe")' in body
    assert PIN in body and "state root" in body and "operation ID" in body
    assert "cleanup owner" in body and "Docker endpoint" in body
    assert "no in-place update" in body
    assert "timeout" in body and "running" in body and "replay" in body
    assert "stdout_truncated" in body or "truncation flags" in body
    assert "Built images" in body


def test_setup_does_not_treat_skill_install_advice_as_authority():
    body = norm(text("agents/setup-digital-twin.md"))
    assert "not authorization to install globally" in body
    assert "No daemon installation" in body
    assert "do not load legacy instructions" in body
    assert "do not silently reorder" in body
    assert "Do not update a selected pin automatically" in body
    assert "host queue or global capacity guard" in body


def test_validator_requires_complete_handoff_and_source_join():
    body = norm(text("agents/validator.md"))
    assert "unsupported-binding: incomplete execution handoff" in body
    assert "Version equality alone cannot show local bytes were installed" in body
    assert "Real-data audits require an explicitly authorized source and separate invocation" in body
    assert "no host home, credentials or Docker socket" in body


def test_core_is_installed_explicitly_not_via_version_bump():
    body = text("context/amplifier-ecosystem-map.md")
    assert "explicit direct source requirement" in body
    assert "Do not bump" in body
    assert "does not implement `pypi_overrides`" in body


def test_historical_evaluation_refuses_without_provisioning():
    result = subprocess.run(["bash", str(ROOT / ".amplifier/evaluations/01-setup-with-build-up-foundation/run.sh")], capture_output=True, text=True, timeout=5)
    assert result.returncode == 2
    assert "unsupported-binding: historical Incus evaluation" in result.stderr
    assert not result.stdout


def test_lifecycle_runner_requires_explicit_scope_and_has_no_replay_loop():
    body = text("tests/run_smart_dtu_lifecycle.py")
    for option in ("docker-host", "daemon-id", "state-root", "operation-id", "owner", "evidence", "python-image"):
        assert f'parser.add_argument("--{option}"' in body
    assert "existing evidence identifies an earlier attempt" in body
    assert "state root must be empty" in body
    assert body.count("lib.launch(PROFILE,") == 1
    assert body.index("lib.stop(uid") < body.index("lib.export_files(uid") < body.index("lib.destroy(uid")
    assert "destroyed.require_removed()" in body
    assert "if not stopped.complete" in body
    assert "baseline_disappeared" in body


def test_no_legacy_default_in_always_on_awareness():
    body = text("context/amplifier-tester-awareness.md")
    assert "Docker Compose" in body
    assert "may create/reuse Gitea" not in body
    assert "Incus" not in body
    assert len(body) <= 1242
