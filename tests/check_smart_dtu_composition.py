"""Installed, no-model composition check, invoked inside the owned Compose twin.

Not a pytest test: dependencies and source roots are explicit in the live runner.
It loads the real Foundation bundle and actual tool-skills resolver; no substitute
bundle loader or mocked subprocess success is used.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import importlib.metadata
import json
from pathlib import Path
import subprocess

PIN = "88d9d84149eee914372c1ca8d68e9eb9f4ba3290"
SKILL_SOURCE = (
    "git+https://github.com/microsoft/amplifier-smart-tool-digital-twin-universe@"
    + PIN + "#subdirectory=skills"
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


async def check(tester: Path, foundation: Path, evidence: Path) -> dict:
    import amplifier_core
    import amplifier_core._engine
    import amplifier_foundation
    from amplifier_foundation import Bundle, BundleRegistry, load_bundle
    from amplifier_module_tool_skills import SkillsTool, _resolve_skill_sources

    registry = BundleRegistry(home=evidence / "registry", persist=False, read_persisted=False)
    registry.register({"foundation": str(foundation)})
    behavior = await load_bundle(str(tester / "behaviors/amplifier-tester.yaml"), registry=registry)
    root = await load_bundle(str(tester / "bundle.md"), registry=registry)
    assert behavior.instruction is None
    assert set(behavior.agents) == {"amplifier-tester:setup-digital-twin", "amplifier-tester:validator"}
    assert set(root.agents) == set(behavior.agents)
    assert not behavior.providers and not behavior.session
    host = Bundle(
        name="synthetic-selected-host", instruction="Preserve this selected host instruction.",
        session={"orchestrator": "selected-orchestrator", "context": "selected-context"},
        providers=[{"module": "selected-provider", "config": {"sentinel": "no-credential"}}],
    )
    composed = host.compose(behavior)
    assert composed.instruction == host.instruction
    assert composed.providers == host.providers
    assert composed.session == host.session
    assert composed.source_base_paths["amplifier-tester"] == tester
    context_text = "\n".join(path.read_text() for path in composed.context.values())
    assert "Docker Compose DTUs" in context_text
    assert "Incus" not in context_text
    assert "amplifier-gitea" not in context_text
    assert "may create/reuse Gitea" not in context_text
    assert not any("digital-twin-universe:" in name for name in composed.agents)
    tools = composed.to_mount_plan()["tools"]
    assert [tool["module"] for tool in tools] == ["tool-skills"]
    config = dict(tools[0]["config"])
    assert config["skills"] == [SKILL_SOURCE]
    config["cache_dir"] = str(evidence / "skills-cache")
    origins: dict[Path, str] = {}
    dirs, pending = await _resolve_skill_sources(config, None, origins)
    assert not pending and len(dirs) == 1
    tool = SkillsTool(config, resolved_dirs=dirs)
    info = await tool.execute({"info": "digital-twin-universe"})
    loaded = await tool.execute({"skill_name": "digital-twin-universe"})
    assert info.success and loaded.success
    assert "Docker Compose" in loaded.output["content"]
    assert "amplifier-digital-twin" not in loaded.output["content"]
    assert "metadata" in (dirs[0] / "digital-twin-universe/SKILL.md").read_text()
    skill_commit = subprocess.check_output(["git", "-C", str(dirs[0]), "rev-parse", "HEAD"], text=True).strip()
    assert skill_commit == PIN

    # Counterexample: a separately included old behavior's source still wins.
    # This tests discovery precedence, not new authority to execute that backend.
    legacy = evidence / "legacy-skills"
    legacy_skill = legacy / "digital-twin-universe/SKILL.md"
    legacy_skill.parent.mkdir(parents=True)
    legacy_skill.write_text(
        "---\nname: digital-twin-universe\ndescription: Legacy counterexample\n---\n"
        "Legacy Incus manual counterexample; never execute.\n"
    )
    colliding = Bundle(name="legacy-host-include", tools=[{
        "module": "tool-skills", "config": {"skills": [str(legacy)]},
    }]).compose(behavior)
    collision_config = colliding.to_mount_plan()["tools"][0]["config"]
    assert collision_config["skills"] == [str(legacy), SKILL_SOURCE]
    collision_tool = SkillsTool(collision_config, resolved_dirs=[legacy, *dirs])
    collision_info = await collision_tool.execute({"info": "digital-twin-universe"})
    assert collision_info.success
    assert collision_tool.skills["digital-twin-universe"].path == legacy_skill
    setup = (tester / "agents/setup-digital-twin.md").read_text()
    assert setup.index('load_skill(info="digital-twin-universe")') < setup.index("load the skill")
    assert "do not load legacy instructions" in setup

    foundation_source = foundation / "amplifier_foundation/__init__.py"
    foundation_installed = Path(amplifier_foundation.__file__)
    assert sha(foundation_source) == sha(foundation_installed)
    direct_url = json.loads(importlib.metadata.distribution("amplifier-foundation").read_text("direct_url.json"))
    native = {
        "foundation_version": importlib.metadata.version("amplifier-foundation"),
        "foundation_path": str(foundation_installed), "foundation_file_sha256": sha(foundation_installed),
        "foundation_direct_url": direct_url,
        "core_version": importlib.metadata.version("amplifier-core"),
        "core_path": str(Path(amplifier_core.__file__)),
        "core_native_path": str(Path(amplifier_core._engine.__file__)),
    }
    prompt = composed.instruction + "\n\n" + context_text
    (evidence / "composed-head.txt").write_text(prompt)
    (evidence / "resolved-agents.json").write_text(json.dumps(composed.agents, indent=2, default=str))
    (evidence / "mount-plan.json").write_text(json.dumps(composed.to_mount_plan(), indent=2, default=str))
    return {
        "native_imports": native, "agents": sorted(composed.agents),
        "contexts": {key: str(path) for key, path in composed.context.items()},
        "namespace_roots": {key: str(path) for key, path in composed.source_base_paths.items()},
        "selected_host_preserved": True, "skill_commit": skill_commit,
        "skill_sources": {str(key): value for key, value in origins.items()},
        "skill_info": info.output, "skill_load": loaded.output,
        "collision_info": collision_info.output, "collision_detected": True,
        "head_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
        "limits": ["No model dispatch or live provider call", "Not a real user host activation"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tester", type=Path, required=True)
    parser.add_argument("--foundation", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    result = asyncio.run(check(args.tester.resolve(), args.foundation.resolve(), args.evidence.resolve()))
    (args.evidence / "composition.json").write_text(json.dumps(result, indent=2, default=str))
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
