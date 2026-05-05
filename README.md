
# CVDLink (FeatureCloud extension)

## Overview

**CVDLink** is a domain-specific extension of the **FeatureCloud** Python package, tailored for the **CVDLink** project and deployment at [https://fc.cvdlink-project.eu](https://fc.cvdlink-project.eu). It builds on the same engine to support **privacy-preserving federated learning and data analysis**, with **CVDLink-oriented defaults** for controller images, global API endpoints, and container registries.

CVDLink targets federated collaborations in cardiovascular research and related biomedical domains, enabling partners to run distributed workflows without sharing raw data.

> **Important:** CVDLink is **not** a standalone replacement for FeatureCloud. It is a **specialization** of the same codebase and tooling, distributed as the **`cvdlink`** pip package with CVDLink-first defaults.

---

## Relationship to FeatureCloud

This package reuses the FeatureCloud controller runtime, app model, CLI layout, tests, and workflow tooling. It adds:

- **`cvdlink` / `CVDLink` CLI entry points** that default to the **CVDLink** profile
- **`featurecloud` / `FeatureCloud` entry points** that default to the **FeatureCloud** profile (same commands, different defaults)
- **Profile-aware Docker image names** for app **publish**, **download**, **remove**, and **test** flows (registry host prefix chosen from the active profile)
- Optional **`--no-pull`** on **controller start** for air-gapped or pre-loaded images

For general FeatureCloud concepts and app development, see [featurecloud.ai](https://featurecloud.ai) and the [FeatureCloud repository](https://github.com/FeatureCloud/FeatureCloud).

Reference: Matschinske, J., Späth, J., Bakhtiari, M., Probul, N., Kazemi Majdabadi, M. M., Nasirigerdeh, R., ... & Baumbach, J. (2023). The FeatureCloud platform for federated learning in biomedicine: unified approach. *Journal of Medical Internet Research*, 25, e42621.

---

## Installation

```bash
pip install cvdlink
```

The distribution name on PyPI is **`cvdlink`**; import paths remain under **`FeatureCloud`**.

---

## CLI entry points and profiles

| Command | Default profile | Typical use |
|--------|-----------------|-------------|
| `cvdlink` / `CVDLink` | `cvdlink` | CVDLink deployments (`fc.cvdlink-project.eu`, …) Same flags as FeatureCloud. |
| `featurecloud` / `FeatureCloud` | `featurecloud` | Upstream FeatureCloud defaults (`featurecloud.ai`, …) |

The active profile affects **default registry prefixes** for app images:

- **FeatureCloud:** `featurecloud.ai/…`
- **CVDLink:** `fc.cvdlink-project.eu/…`

You can still override the registry with **`--registry`** where the command supports it. Short image names are completed using the prefix that matches the current profile (so you do not have to type the full registry path when it matches your environment).

### Environment variable

For **tests** and **workflow** code that resolves app images outside the main CLI, you can set:

```bash
export FC_CLI_PROFILE=cvdlink   # or featurecloud
```

If unset, the workflow layer falls back to sensible defaults for the context in which it runs.

---

## Controller commands

Start, stop, inspect, and tail controller instances.

### Start a controller

```bash
cvdlink controller start [NAME] [OPTIONS]
```

By default, CVDLink uses profile **`cvdlink`**: CVDLink-oriented controller images and config defaults apply unless you override them.

#### Common options

- **`--port`** — Controller port (default: `8000`)
- **`--data-dir`** — Data directory for the controller
- **`--controller-image`** — Full image reference override
- **`--global-endpoint`**, **`--registry`**, **`--relay-address`** — Override baked config
- **`--poll-interval`**, **`--query-interval`** — Workflow timing overrides
- **`--config-file`** — Config file path inside the container
- **`--no-pull`** — Skip **`docker pull`**; use the controller image already present locally (offline mirrors, custom tags, or CI)

Example:

```bash
cvdlink controller start --data-dir ./data
cvdlink controller start --no-pull --controller-image fc.cvdlink-project.eu/controller:latest
```

### Other controller commands

- `controller status`, `logs`, `tail`, `ls`, `stop`

---

## App commands

Create, build, publish, pull, and remove federated app images.

### Examples

```bash
cvdlink app new --template-name app-blank
cvdlink app build --path <APP_PATH> --image-name <NAME> --tag <TAG>
cvdlink app publish --name <NAME> --tag <TAG>
```

**Publish / download / remove** use the **registry prefix for the active CLI profile** unless you supply a fully qualified image name. Log in to the registry host you use (`docker login fc.cvdlink-project.eu` for CVDLink).

Other subcommands include **`download`**, **`remove`**, **`plot-states`**, matching FeatureCloud semantics under the chosen profile.

---

## Tests and workflow

**`cvdlink test`** (and **`featurecloud test`**) use the same test harness; image names for **`test start`** respect the active profile (and **`FC_CLI_PROFILE`** when workflow code runs in isolation). Use this when validating apps against the registry naming you deploy with.

---

## Branch purpose (**`cvdlink`**)

The **`cvdlink`** branch exists to ship a **single package** that:

1. Keeps **feature parity** with the FeatureCloud CLI and libraries.
2. Makes **CVDLink** the default when users install **`cvdlink`** and run **`cvdlink …`**.
3. Avoids **blind `docker pull`** when operators choose **`--no-pull`**.
4. Keeps **registry-qualified image names** consistent with **CVDLink** vs **FeatureCloud** infrastructure.

Upstream FeatureCloud behavior remains available via the **`featurecloud`** entry points in the same installation.
