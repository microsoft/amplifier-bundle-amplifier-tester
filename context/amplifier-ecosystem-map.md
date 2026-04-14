# Amplifier Ecosystem Map for Validation

This map helps the change-analyzer agent classify repos and generate the
correct DTU profile strategy.


## Repo Classification

| Repo | Layer | Profile strategy |
|------|-------|------------------|
| `amplifier-core` | core | `pypi_overrides` with `wheel_from_git` (Rust+Python wheel build) |
| `amplifier` | cli | `url_rewrites` for CLI install source |
| `amplifier-app-cli` | cli | `url_rewrites` for CLI install source |
| `amplifier-foundation` | foundation | `url_rewrites` (anything depending on foundation gets local version) |
| `amplifier-module-*` | module | `url_rewrites` for the module |
| `amplifier-bundle-*` | bundle | `url_rewrites` + explicit `amplifier bundle add` in provision |


## Dependency Hierarchy

Changes flow downward. A change at a lower level affects everything above it.

```
amplifier (CLI entry point)
  |
  +-- amplifier-app-cli (reference CLI app)
  |     |
  |     +-- amplifier-foundation (bundle primitives, utilities)
  |     |
  |     +-- amplifier-core (kernel, contracts, session lifecycle)
  |           |
  |           +-- amplifier-module-* (all modules depend only on core)
  |
  +-- amplifier-bundle-* (bundles compose modules + context + agents)
```

**Implications for profile generation:**
- Changing `amplifier-core` means every module, the CLI, and foundation may
  be affected. The profile should install from Gitea/PyPI override and run
  a broad smoke test.
- Changing a module only affects sessions using that module. The profile
  needs `url_rewrites` for just that module.
- Changing a bundle only affects sessions with that bundle added. The profile
  needs `url_rewrites` + `bundle add`.


## Core is Special

`amplifier-core` is the only ecosystem repo published to PyPI. All other repos
are installed from git. This means:

- **Core changes** require `pypi_overrides` with `wheel_from_git` because the
  Amplifier install process (`uv tool install git+.../amplifier`) resolves
  `amplifier-core` from PyPI, not from git.
- **Everything else** uses `url_rewrites` to redirect `github.com/microsoft/...`
  to the Gitea instance, which is sufficient because they install from git URLs.

The `wheel_from_git` config for core:
```yaml
pypi_overrides:
  packages:
    - name: amplifier-core
      wheel_from_git:
        repo: ${GITEA_URL}/admin/amplifier-core.git
        ref: main
        username: admin
        token_var: GITEA_TOKEN
        build_cmd: uv run --with maturin maturin build --release
        wheel_glob: target/wheels/amplifier_core-*.whl
```


## Provider Configuration

Every DTU profile for amplifier tester needs a configured LLM provider
for smoke tests. The standard configuration:

```yaml
passthrough:
  allow_external: true
  services:
    - name: anthropic
      key_env: ANTHROPIC_API_KEY
```

And in the provision setup_cmds:
```yaml
- |
  mkdir -p /root/.amplifier
  cat > /root/.amplifier/settings.yaml << EOF
  config:
    providers:
      - module: provider-anthropic
        source: git+https://github.com/microsoft/amplifier-module-provider-anthropic@main
        config:
          api_key: $ANTHROPIC_API_KEY
  EOF
```

**Important:** If `amplifier-module-provider-anthropic` is among the changed
repos, the `source:` line in settings.yaml still points to `github.com` because
the DTU's `url_rewrites` transparently redirect it to Gitea. No special handling
needed in settings.yaml.


## Common Multi-Repo Combinations

| Scenario | Repos | Strategy |
|----------|-------|----------|
| Core API change + module update | `amplifier-core` + `amplifier-module-*` | `pypi_overrides` for core + `url_rewrites` for module |
| Bundle with new agent | `amplifier-bundle-*` | `url_rewrites` + `bundle add` |
| Foundation change | `amplifier-foundation` | `url_rewrites` for foundation |
| Full stack | `amplifier-core` + `amplifier-foundation` + module(s) + bundle(s) | All strategies combined in one profile |
