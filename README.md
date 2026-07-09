
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
- **Profile-aware Docker image names** for app **build**, **publish**, **download**, **remove**, and **test** flows (registry host prefix chosen from the active profile)
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

**`app build`** tags the image locally as `<name>:<tag>` and, for the active CLI profile, also as `<registry>/<name>:<tag>` (e.g. `fc.cvdlink-project.eu/my_app:latest` under `cvdlink`). This aligns **`build`** with **`test start`**, **`publish`**, **`download`**, and **`remove`**, which already use registry-qualified names.

**Publish / download / remove** use the **registry prefix for the active CLI profile** unless you supply a fully qualified image name. Log in to the registry host you use (`docker login fc.cvdlink-project.eu` for CVDLink).

Other subcommands include **`download`**, **`remove`**, **`plot-states`**, matching FeatureCloud semantics under the chosen profile.

---

## Tests and workflow

**`cvdlink test`** (and **`featurecloud test`**) use the same test harness; image names for **`test start`** respect the active profile (and **`FC_CLI_PROFILE`** when workflow code runs in isolation). Use this when validating apps against the registry naming you deploy with.

### Local testbed example

```bash
cvdlink app build <APP_PATH> my_app latest True
cvdlink test start --app-image my_app --client-dirs './01,./02'
```

After **`app build`**, you can use the short image name with **`test start`**; the registry alias tag is created automatically.

---

## Running apps on the CVDLink platform

For running apps via [https://fc.cvdlink-project.eu/projects](https://fc.cvdlink-project.eu/projects) (frontend project workflow), use a registry image and point the controller at your input data:

```bash
git clone https://github.com/Freddsle/fc_sending_examples.git
cd fc_sending_examples
pip install cvdlink
cvdlink controller start --data-dir ./data
cvdlink app download fc.cvdlink-project.eu/fc_sending_examples
```

Then create a project on the platform, add the app, select input data via the frontend, and run.

### Platform project vs local testbed

| Workflow | Image source | How data is supplied |
|----------|--------------|----------------------|
| **Platform project** (frontend) | `app download` with registry-qualified name | Select client files in the CVDLink web UI |
| **Local testbed** (`test start`) | `app build` or `app download` | `--client-dirs` / `--generic-dir` CLI flags |

### `--data-dir` vs `--mount`

- **`--data-dir ./data`** (recommended): mounts the host `data/` folder as the controller's data root. Client input folders (e.g. `data/01`, `data/02`) should live here so the platform can access them when you select files in the GUI.
- **`--mount <path>`**: mounts an *additional* host path at `/mnt` inside the container, intended for protected uploads. It does **not** replace `--data-dir`. If input data is only reachable via `--mount` and not under the controller data root, file selection in the frontend may fail or return an empty `"files": []` payload.

```bash
cvdlink controller start --data-dir ./data
# optional extra mount (data must still be visible to the controller):
cvdlink controller start --data-dir ./data --mount /absolute/path/to/extra-data
```

### Browser recommendation

For selecting input data and running apps in the CVDLink web UI, **Firefox** is the recommended browser. If file selection or upload does not behave as expected in another browser (e.g. Chrome), try Firefox before changing your controller or data setup.

### If file selection returns empty `"files": []`

1. Use `--data-dir` pointing at the folder that contains client subdirectories (e.g. `./data` with `01/`, `02/` inside).
2. Try the platform GUI in Firefox.
3. Use `app download` with the registry-qualified image name for platform projects.
4. If problems persist, verify the controller is running and data paths are visible (`cvdlink controller status`).

---

## Branch purpose (**`cvdlink`**)

The **`cvdlink`** branch exists to ship a **single package** that:

1. Keeps **feature parity** with the FeatureCloud CLI and libraries.
2. Makes **CVDLink** the default when users install **`cvdlink`** and run **`cvdlink …`**.
3. Avoids **blind `docker pull`** when operators choose **`--no-pull`**.
4. Keeps **registry-qualified image names** consistent with **CVDLink** vs **FeatureCloud** infrastructure.

Upstream FeatureCloud behavior remains available via the **`featurecloud`** entry points in the same installation.
