# Amplifier Ecosystem Map for Validation

Classify the approved source scope before writing a Docker Compose Smart Tool
profile. Read the selected `digital-twin-universe` installation's manifest and
`docs/03-profile.md`; the legacy Incus schema is not compatible.

## Repo classification

| Repo | Layer | Profile strategy |
|------|-------|------------------|
| `amplifier-core` | core | `x-dtu.repositories` plus a guest-built local wheel or explicit direct source requirement in the actual install environment |
| `amplifier`, `amplifier-app-cli` | cli | Snapshot each changed repo; install from its ordinary HTTPS Git URL |
| `amplifier-foundation` | foundation | Snapshot the repo; verify installed loader/composition behavior |
| `amplifier-module-*` | module | Snapshot the module; verify actual import/mount and affected behavior |
| `amplifier-bundle-*` | bundle/prompt | Snapshot the bundle; compose the behavior into the user's selected host and inspect resolved agents, skills, contexts and instruction |

`x-dtu.repositories` entries pair a local repository `path` (relative to the
profile) with its original HTTPS `url`. The Smart Tool snapshots approved tracked
and nonignored untracked bytes into its own Gitea sidecar; the source checkout is
never mounted into the guest or changed. Keep snapshot tree/commit receipts and
compare installed bytes. For shallow repos, use the checked-out branch actually
served, not an assumed `main`. Other repositories still resolve upstream.

## Dependency hierarchy

```text
amplifier -> amplifier-app-cli -> amplifier-foundation + amplifier-core
amplifier-module-* -> amplifier-core
amplifier-bundle-* -> selected modules, contexts and agents
```

A core change can affect every layer above it. Select checks for the affected
contract rather than calling one version check a full-stack qualification.
Multi-repo changes need all affected source joins in the same environment. Label
candidate dependency graphs separately from accepted upstream revisions.

## Core needs explicit installation

Serving a core Git repository does not redirect a dependency resolved from PyPI.
The Smart Tool does not implement `pypi_overrides` or `wheel_from_git` keys. Build
the approved core source with its documented build process inside the guest/build,
then install that exact wheel or direct source requirement in the app environment.
A find-links directory alone may lose to a newer index version. Do not bump the
user's version to win resolution. Verify native import, distribution version,
installed path and wheel/source identity in the interpreter the app actually uses.
See the pinned Smart Tool's `examples/amplifier-modules-dtu` for build/TLS mechanics,
not its optional provider defaults or version-bump suggestion.

## Provider and private-repository access

Default checks are deterministic and use **no provider credentials or model calls**.
Never copy host settings, history or credential directories. Preserve the user's
chosen host/base and provider only when needed for an explicitly scoped check,
in synthetic settings with literal environment references. Missing credentials
are a blocker, not permission to choose Anthropic or another provider.

For separately authorized live access, forward only required runtime environment
names, never secret values in settings, logs, profile URLs or build args. Use
supported build secrets when a private install actually needs them. `GH_TOKEN`
is not forwarded for public snapshots. Gitea and gateway belong to the new exact
Compose project; never reuse a peer's server or token.

## Re-test and dispose

There is no in-place update. Export evidence, stop and remove the owned old project,
then snapshot changed source under a new explicit test operation. Never rename or
replay an uncertain operation. Preserve the full endpoint/state/operation binding
through validation and cleanup, including the named cleanup owner and budget.

`bundle add --app` composes a behavior; plain `bundle add` only registers it and
`bundle use` replaces the base. A bundle listing is not composition proof. Legacy
Incus instances require their original operator/interface and are never inferred
from an ID or adopted into Docker.
