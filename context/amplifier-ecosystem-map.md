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

Generated profiles should mirror the user's host `~/.amplifier/settings.yaml`
`config.providers` block rather than hard-coding a single provider. One
`passthrough.services` entry is emitted per env var referenced by the
host's providers. The `config.providers` block is then written verbatim
into the in-DTU `/root/.amplifier/settings.yaml` via a heredoc that
expands `${VAR}` references using the passthrough'd values.

If a provider module is among the changed repos, the `source:` URL still
points at `github.com` -- `url_rewrites` transparently redirects it to
Gitea. No special handling needed.

See setup-digital-twin step 5 for the full process and the
`amplifier-module-provider-anthropic` default for hosts without a
`~/.amplifier/settings.yaml`.


## GitHub Credential Forwarding

`GH_TOKEN` is forwarded only when the scenario requires private repo
access detailed in `agents/setup-digital-twin.md`


## Common Multi-Repo Combinations

| Scenario | Repos | Strategy |
|----------|-------|----------|
| Core API change + module update | `amplifier-core` + `amplifier-module-*` | `pypi_overrides` for core + `url_rewrites` for module |
| Bundle with new agent | `amplifier-bundle-*` | `url_rewrites` + `bundle add` |
| Foundation change | `amplifier-foundation` | `url_rewrites` for foundation |
| Full stack | `amplifier-core` + `amplifier-foundation` + module(s) + bundle(s) | All strategies combined in one profile |
