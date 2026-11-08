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
import os
from pathlib import Path

PIN = "88d9d84149eee914372c1ca8d68e9eb9f4ba3290"
SKILL_SOURCE = (
    "git+https://github.com/microsoft/amplifier-smart-tool-digital-twin-universe@"
    + PIN + "#subdirectory=skills"
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


async def check(tester: Path, foundation: Path, evidence: Path) -> dict:
    if not __debug__:
        raise RuntimeError("Run without Python optimization: assertions are required checks")
    import amplifier_core
    import amplifier_core._engine
    import amplifier_foundation
    from amplifier_core import AmplifierSession
    from amplifier_foundation import Bundle, BundleRegistry, load_bundle
    from amplifier_foundation.bundle import PreparedBundle, BundleModuleResolver
    from amplifier_module_tool_skills import SkillsTool, mount

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
    composed.resolve_pending_context()
    composed.load_agent_metadata()
    assert not composed._pending_context
    for name in composed.agents:
        assert composed.resolve_agent_path(name).is_file()
        assert composed.agents[name]["description"].startswith("USE WHEN")
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
    # Shared-store mode supports immutable commit sources. Older skills caches
    # use git clone --branch <ref> and cannot resolve a raw commit on first load.
    # Keep this test-private and report the mode, not blanket host compatibility.
    os.environ["AMPLIFIER_SOURCE_STORE"] = str(evidence / "source-store")
    session = AmplifierSession(config={"session": {
        "orchestrator": "unused-no-model", "context": "unused-no-model",
    }})
    cleanup = await mount(session.coordinator, config)
    tool = session.coordinator.get("tools", "load_skill")
    dirs = tool.skills_dirs
    assert not tool._pending_mention_sources and len(dirs) == 1
    assert tool.skills["digital-twin-universe"].source == SKILL_SOURCE
    assert tool.skills["digital-twin-universe"].trusted is False
    info = await tool.execute({"info": "digital-twin-universe"})
    loaded = await tool.execute({"skill_name": "digital-twin-universe"})
    assert info.success and loaded.success
    assert "Docker Compose" in loaded.output["content"]
    assert "amplifier-digital-twin" not in loaded.output["content"]
    assert "metadata" in (dirs[0] / "digital-twin-universe/SKILL.md").read_text()
    # Shared-store immutable objects may not carry a .git directory. Source
    # identity is the pinned resolver URI + bytes compared with the served pin.
    skill_file_sha256 = sha(dirs[0] / "digital-twin-universe/SKILL.md")

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
    skills_direct_url = json.loads(importlib.metadata.distribution("amplifier-module-tool-skills").read_text("direct_url.json"))
    native = {
        "foundation_version": importlib.metadata.version("amplifier-foundation"),
        "foundation_path": str(foundation_installed), "foundation_file_sha256": sha(foundation_installed),
        "foundation_direct_url": direct_url,
        "skills_direct_url": skills_direct_url,
        "core_version": importlib.metadata.version("amplifier-core"),
        "core_path": str(Path(amplifier_core.__file__)),
        "core_native_path": str(Path(amplifier_core._engine.__file__)),
    }
    prepared = PreparedBundle(
        mount_plan=composed.to_mount_plan(), resolver=BundleModuleResolver({}), bundle=composed,
    )
    prompt = await prepared.create_system_prompt_factory(session, session_cwd=evidence)()
    assert prompt.startswith(host.instruction)
    assert "Docker Compose DTUs" in prompt and "Incus" not in prompt
    (evidence / "composed-head.txt").write_text(prompt)
    (evidence / "resolved-agents.json").write_text(json.dumps(composed.agents, indent=2, default=str))
    (evidence / "mount-plan.json").write_text(json.dumps(composed.to_mount_plan(), indent=2, default=str))
    if cleanup:
        await cleanup()
    return {
        "native_imports": native, "agents": sorted(composed.agents),
        "contexts": {key: str(path) for key, path in composed.context.items()},
        "namespace_roots": {key: str(path) for key, path in composed.source_base_paths.items()},
        "selected_host_preserved": True, "skill_requested_commit": PIN,
        "skill_file_sha256": skill_file_sha256, "skill_resolution": "guest-private shared source store",
        "skill_info": info.output, "skill_load": loaded.output,
        "collision_info": collision_info.output, "collision_detected": True,
        "head_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
        "limits": ["No model dispatch or live provider call", "Not a real user host activation", "Legacy skills cache cannot resolve the commit pin on a first clone"],
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
