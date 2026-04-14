# Amplifier Bundle Amplifier Tester

Validates Amplifier ecosystem changes (bundles, modules, prompts, app-cli, core, foundation) in isolated [Digital Twin Universe](https://github.com/microsoft/amplifier-bundle-digital-twin-universe) environments before they reach real users.

The bundle dynamically generates the right profile based on what you actually changed using an agent.
Then the ecosystem validator mirrors your local repos to Gitea, builds the correct `url_rewrites` and `pypi_overrides`, launches a DTU, and runs validation checks.

![Architecture](docs/amplifier-tester-architecture.svg)


## Prerequisites

This bundle depends on the Digital Twin Universe bundle (which itself depends on
[amplifier-bundle-gitea](https://github.com/microsoft/amplifier-bundle-gitea)).
See their READMEs for prerequisite setup:

- [Digital Twin Universe prerequisites](https://github.com/microsoft/amplifier-bundle-digital-twin-universe#prerequisites)
- [Gitea prerequisites](https://github.com/microsoft/amplifier-bundle-gitea#prerequisites)


## Installation

`--app` composes the bundle onto every Amplifier session. Remove it to only register the bundle for later activation with `amplifier bundle use`.

```bash
amplifier bundle add git+https://github.com/microsoft/amplifier-bundle-amplifier-tester@main --app
```

To compose into an existing bundle:
```bash
amplifier bundle add "git+https://github.com/microsoft/amplifier-bundle-amplifier-tester@main#subdirectory=behaviors/amplifier-tester.yaml" --app
```


## What It Validates

- **Core** (`amplifier-core`) -- PyPI override with a locally built wheel, version check, Python import check
- **Module** (`amplifier-module-*`) -- URL rewrite to Gitea, smoke test exercises the module
- **Bundle** (`amplifier-bundle-*`) -- URL rewrite + `bundle add`, verify bundle loads and agents are available
- **CLI** (`amplifier`, `amplifier-app-cli`) -- URL rewrite for install source, help + smoke test
- **Foundation** (`amplifier-foundation`) -- URL rewrite, bundle loading works
- **Prompt/context** (agent `.md` or context files in a bundle) -- same as bundle, since prompt changes live in bundles
- **Multi-repo** (any combination of the above) -- all strategies combined in a single profile


## Agents

- **[Setup Digital Twin](agents/setup-digital-twin.md)** -- gathers context from the user and/or workspace, classifies changes, mirrors to Gitea, generates a DTU profile, launches and verifies the environment.
- **[Ecosystem Validator](agents/validator.md)** -- runs targeted validation checks inside the DTU and reports pass/fail results.


## Typical Flow

```
"Validate my changes to ~/repos/amplifier-module-provider-anthropic"
```

1. **setup-digital-twin** inspects the repo, classifies it as a module change
2. Reuses or creates a Gitea instance, mirrors from GitHub, pushes local changes on top
3. Generates a DTU profile with the correct `url_rewrites`
4. Launches the DTU -- Amplifier installs inside thinking it's pulling from upstream
5. Verifies: CLI starts, provider loads, smoke test passes
6. Reports results

For multi-repo changes:
```
"Validate my changes to ~/repos/amplifier-core and ~/repos/amplifier-module-provider-anthropic"
```

Both repos get mirrored. A single profile is generated with `pypi_overrides` for core
AND `url_rewrites` for the module. One DTU tests everything together.


## Re-testing After Fixes

The generated DTU profiles include an `update` section. After fixing an issue:

1. Commit the fix locally
2. Push to Gitea (`git push gitea HEAD:main --force`)
3. `amplifier-digital-twin update <instance-id>`
4. Re-run validator

No need to destroy and relaunch.


## Scope

**In scope:** Amplifier ecosystem repos -- core, foundation, modules, bundles, app-cli.

**Out of scope:** Arbitrary user apps (use [reality-check](https://github.com/microsoft/amplifier-bundle-reality-check) for that),
mock services, browser-based UI testing, resolver integration.
