"""Opt-in real Smart Tool lifecycle for the fixed tester self-validation profile.

Run on the selected Docker daemon's host. Uses one owned Compose project plus
its generated Gitea/gateway sidecars, no credentials/model calls. This is a test,
not a backend adapter, scheduler, or generic profile generator. It never resumes
or replays a previous operation. Keep failed receipts and inspect known ownership.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys

PIN = "88d9d84149eee914372c1ca8d68e9eb9f4ba3290"
ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / ".agents/digital-twin-universe/amplifier-tester-self-validation/compose.yaml"
URLS = {
    "tester": "https://github.com/microsoft/amplifier-bundle-amplifier-tester",
    "foundation": "https://github.com/microsoft/amplifier-foundation",
    "skills": "https://github.com/microsoft/amplifier-bundle-skills",
    "smart_tool": "https://github.com/microsoft/amplifier-smart-tool-digital-twin-universe",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(directory: Path, name: str, value) -> None:
    if hasattr(value, "model_dump"):
        value = value.model_dump(mode="json")
    with (directory / name).open("x") as stream:
        json.dump(value, stream, indent=2, default=str)
        stream.write("\n")


def checked(argv: list[str], timeout: int = 60) -> str:
    return subprocess.check_output(argv, text=True, stderr=subprocess.STDOUT, timeout=timeout).strip()


def execute(lib, uid: str, config, evidence: Path, stage: str, command: str, timeout: int = 300):
    save(evidence, stage + "-request.json", {"command": command, "timeout": timeout})
    result = lib.execute(uid, command, timeout_seconds=timeout, max_output_bytes=1048576, config=config)
    save(evidence, stage + ".json", result)
    if result.exit_code != 0 or result.stdout_truncated or result.stderr_truncated:
        raise RuntimeError(f"{stage}: exit={result.exit_code}; inspect both retained streams/truncation")
    return result


def main() -> int:
    if not __debug__:
        raise RuntimeError("Run without Python optimization: assertions are required checks")
    parser = argparse.ArgumentParser(description=__doc__)
    for source in URLS:
        parser.add_argument("--" + source.replace("_", "-") + "-repo", type=Path, required=True)
    parser.add_argument("--docker-host", required=True)
    parser.add_argument("--daemon-id", required=True)
    parser.add_argument("--state-root", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True, help="new directory outside all served repos")
    parser.add_argument("--operation-id", required=True)
    parser.add_argument("--owner", required=True)
    parser.add_argument("--python-image", required=True, help="Debian-based Python image pinned @sha256")
    args = parser.parse_args()
    if not args.docker_host.startswith("unix:///"):
        parser.error("this source-snapshot fixture requires a local Unix Docker socket on the same host")
    os.umask(0o077)
    sources = {key: getattr(args, key + "_repo").resolve() for key in URLS}
    evidence = args.evidence.resolve()
    state_root = args.state_root.resolve()
    if evidence.exists():
        parser.error("existing evidence identifies an earlier attempt; inspect, never replay")
    if state_root.exists() and any(state_root.iterdir()):
        parser.error("state root must be empty; never reset an uncertain operation")
    if "@sha256:" not in args.python_image:
        parser.error("select an immutable approved image digest")
    for source in sources.values():
        if evidence.is_relative_to(source) or state_root.is_relative_to(source):
            parser.error("state/evidence must be outside served sources")
        if checked(["git", "-C", str(source), "rev-parse", "--show-toplevel"]) != str(source):
            parser.error(f"not an exact repository root: {source}")
    if sources["tester"] != ROOT:
        parser.error("run the maintained script from the exact tester checkout being served")
    if checked(["git", "-C", str(sources["smart_tool"]), "rev-parse", "HEAD"]) != PIN:
        parser.error("Smart Tool source must match reviewed pin")
    if checked(["git", "-C", str(sources["smart_tool"]), "status", "--porcelain"]):
        parser.error("Smart Tool reference source must be clean")
    evidence.mkdir(parents=True, mode=0o700)
    executable = Path(sys.executable).parent / "digital-twin-universe"
    if not executable.is_file():
        raise RuntimeError("unsupported-binding: Smart Tool CLI unavailable in selected Python environment")
    from digital_twin_universe import lib
    package = Path(lib.__file__).parent
    direct = json.loads(importlib.metadata.distribution("digital-twin-universe").read_text("direct_url.json"))
    if lib.version() != "0.6.9" or direct.get("vcs_info", {}).get("commit_id") != PIN:
        raise RuntimeError("unqualified installed Smart Tool source; expected pinned 0.6.9")
    for name in ("lib.py", "SMART_TOOL.md"):
        if sha(package / name) != sha(sources["smart_tool"] / "src/digital_twin_universe" / name):
            raise RuntimeError(f"installed source mismatch: {name}")
    config = lib.BackendConfig(state_root=state_root, docker_host=args.docker_host)
    uid = lib.launch_id(args.operation_id, config=config)
    docker = ["docker", "--host", args.docker_host]
    daemon = checked([*docker, "info", "--format", "{{.ID}}"])
    if daemon != args.daemon_id:
        raise RuntimeError("selected daemon identity mismatch")
    for key, source in sources.items():
        os.environ["DTU_" + key.upper() + "_REPO"] = str(source)
    os.environ["DTU_PYTHON_IMAGE"] = args.python_image
    save(evidence, "binding.json", {
        "backend": "smart-tool-docker-compose", "executable": str(executable),
        "library": str(package), "direct_url": direct, "docker_host": args.docker_host,
        "daemon_id": daemon, "state_root": str(state_root), "operation_id": args.operation_id,
        "instance_id": uid, "profile": str(PROFILE), "profile_sha256": sha(PROFILE),
        "dockerfile_sha256": sha(PROFILE.with_name("Dockerfile")),
        "runner_sha256": sha(Path(__file__)), "composition_check_sha256": sha(ROOT / "tests/check_smart_dtu_composition.py"),
        "sources": {key: {"path": str(source), "head": checked(["git", "-C", str(source), "rev-parse", "HEAD"])} for key, source in sources.items()},
        "cleanup_owner": args.owner, "budget": "one twin plus generated Gitea/gateway sidecars",
        "required_checks": ["isolation", "source joins", "native imports", "composition", "local guards", "stop/export/destroy"],
        "limits": ["trusted Compose inputs, not hostile-code sandbox", "proxy allowlist is not an egress firewall", "no live provider or Windows/WSL qualification"],
    })
    helps = {}
    for capability in ("--version", "manifest", "--help", "check", "validate-profile", "launch", "status", "exec", "stop", "export-files", "destroy"):
        argv = [str(executable), capability]
        if not capability.startswith("--") and capability != "manifest":
            argv.append("--help")
        helps[capability] = checked(argv)
    save(evidence, "interface.json", helps)
    ready = lib.check(config)
    save(evidence, "check.json", ready)
    if not ready.ok:
        raise RuntimeError("Smart Tool readiness failed; no install or daemon setup is implied")
    validated = lib.validate_profile(PROFILE, config=config)
    save(evidence, "validate.json", validated)
    if not validated.ok:
        raise RuntimeError("profile validation failed")
    legacy = lib.validate_profile(ROOT / "tests/fixtures/legacy-incus/amplifier-tester-self-validation.yaml", config=config)
    save(evidence, "legacy-profile-negative.json", legacy)
    if legacy.ok:
        raise RuntimeError("legacy Incus profile incorrectly accepted")
    baseline = checked([*docker, "ps", "-aq"]).splitlines()
    save(evidence, "other-containers-before.json", baseline)
    save(evidence, "launch-request.json", {"id": uid, "operation_id": args.operation_id})
    try:
        universe = lib.launch(PROFILE, timeout_seconds=600, operation_id=args.operation_id, config=config)
    except Exception as exc:
        save(evidence, "launch-error.json", {"error": str(exc), "universe_id": getattr(exc, "universe_id", None), "operation_id": getattr(exc, "operation_id", None), "recorded_ids": lib.recorded_ids(config)})
        raise  # Preserve this exact owned attempt for inspection; do not replace it.
    save(evidence, "launch.json", universe)
    if universe.id != uid or universe.state != "running":
        raise RuntimeError("unexpected launch identity/state; inspect exact recorded attempt")
    passed = False
    try:
        container_ids = checked([*docker, "ps", "-aq", "--filter", f"label=com.docker.compose.project={uid}"]).splitlines()
        inventory = json.loads(checked([*docker, "inspect", *container_ids]))
        # Do not retain generated bootstrap passwords in full Docker Config.Env.
        observed = [{"id": item["Id"], "name": item["Name"], "image": item["Image"], "mounts": item["Mounts"], "host_config": {key: item["HostConfig"].get(key) for key in ("Privileged", "PidMode", "NetworkMode", "Binds", "CapAdd", "CapDrop", "Memory", "NanoCpus", "PidsLimit")}, "user": item["Config"]["User"]} for item in inventory]
        save(evidence, "isolation-host.json", observed)
        for item in observed:
            assert not item["host_config"]["Privileged"]
            assert item["host_config"]["PidMode"] != "host"
            assert item["host_config"]["NetworkMode"] != "host"
            for mount in item["mounts"]:
                if mount["Type"] == "bind":
                    assert Path(mount["Source"]).is_relative_to(state_root / uid)
        preflight = "id; printf '\\nHOME=%s\\n' \"$HOME\"; cat /proc/self/mountinfo; test \"$HOME\" = /home/tester && test ! -e /var/run/docker.sock && test ! -e /home/tester/.amplifier/settings.yaml && test ! -e /home/bkrabach"
        execute(lib, uid, config, evidence, "isolation-guest", preflight, 30)
        receipts = {}
        for key, source in sources.items():
            receipt = universe.state_path / "overlay/repositories" / (source.name + ".snapshot.json")
            receipts[key] = json.loads(receipt.read_text())
        save(evidence, "source-snapshots.json", receipts)
        commands = ["mkdir -p /home/tester/src"]
        for key in ("tester", "foundation", "skills"):
            destination = "/home/tester/src/" + key
            commands += [f"git clone {shlex.quote(URLS[key])} {destination}", f"git -C {destination} checkout --detach {receipts[key]['snapshot_commit']}"]
        execute(lib, uid, config, evidence, "clone-snapshots", " && ".join(commands))
        install = "/home/tester/venv/bin/python -m pip install --report /home/tester/evidence/pip-install.json " + " ".join(shlex.quote(value) for value in [
            f"git+{URLS['foundation']}@{receipts['foundation']['snapshot_commit']}",
            f"git+{URLS['skills']}@{receipts['skills']['snapshot_commit']}#subdirectory=modules/tool-skills",
            "pytest==9.1.1",
        ])
        execute(lib, uid, config, evidence, "install", install)
        execute(lib, uid, config, evidence, "composition", "/home/tester/venv/bin/python /home/tester/src/tester/tests/check_smart_dtu_composition.py --tester /home/tester/src/tester --foundation /home/tester/src/foundation --evidence /home/tester/evidence")
        execute(lib, uid, config, evidence, "guards", "cd /home/tester/src/tester && /home/tester/venv/bin/python -m pytest tests/ -q")
        # Source joins for the installed library and cloned candidate tree.
        joined = execute(lib, uid, config, evidence, "source-joins", "git -C /home/tester/src/tester rev-parse HEAD HEAD^{tree}; /home/tester/venv/bin/python -c 'import json, importlib.metadata as m; print(m.distribution(\"amplifier-foundation\").read_text(\"direct_url.json\")); print(m.distribution(\"amplifier-module-tool-skills\").read_text(\"direct_url.json\")); print(json.load(open(\"/home/tester/evidence/composition.json\"))[\"skill_file_sha256\"])'")
        assert receipts["tester"]["snapshot_tree"] in joined.stdout
        assert receipts["foundation"]["snapshot_commit"] in joined.stdout
        assert receipts["skills"]["snapshot_commit"] in joined.stdout
        assert sha(sources["smart_tool"] / "skills/digital-twin-universe/SKILL.md") in joined.stdout
        passed = True
    except Exception as exc:
        save(evidence, "check-error.json", {"error": str(exc), "type": type(exc).__name__})
        raise
    finally:
        stopped = lib.stop(uid, config=config)
        save(evidence, "stop.json", stopped)
        if not stopped.complete:
            raise RuntimeError("stop incomplete; preserve state and notify cleanup owner")
        archive = lib.export_files(uid, "/home/tester/evidence", evidence / "guest-evidence.tar", max_bytes=16777216, config=config)
        save(evidence, "export.json", archive)
        if not passed:
            save(evidence, "retained-failure.json", {"owner": args.owner, "instance_id": uid, "state_root": str(state_root), "reason": "failed/unknown checks: stopped and exported; retain exact project for inspection before explicit cleanup"})
            raise RuntimeError("checks failed; exact stopped project retained for cleanup owner")
        destroyed = lib.destroy(uid, config=config)
        save(evidence, "destroy.json", destroyed)
        destroyed.require_removed()
        remaining_images = json.loads(checked([*docker, "image", "inspect", f"{uid}-tester"]))
        save(evidence, "built-image-retained.json", {"owner": args.owner, "id": remaining_images[0]["Id"], "tags": remaining_images[0]["RepoTags"], "reason": "built images survive destroy; caller owns exact image cleanup"})
        after = checked([*docker, "ps", "-aq"]).splitlines()
        save(evidence, "other-containers-after.json", after)
        save(evidence, "summary.json", {"checks_passed": passed, "stop_complete": stopped.complete, "destroy_complete": destroyed.complete, "baseline_container_ids_still_present": sorted(set(baseline) & set(after)), "baseline_disappeared": sorted(set(baseline) - set(after)), "guest_archive_sha256": archive.sha256})
    print(json.dumps({"checks_passed": passed, "instance_id": uid, "evidence": str(evidence)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
