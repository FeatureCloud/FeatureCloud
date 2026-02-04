
# CVDLink (FeatureCloud Extension)

## Overview

**CVDLink** is a domain-specific extension of the **FeatureCloud** Python package, customized and deployed for the **CVDLink project** available on https://fc.cdvlink-project.eu   
It builds on the core FeatureCloud platform to support **privacy-preserving federated learning and data analysis**, while providing **CVDLink-specific defaults, endpoints, and infrastructure integrations**.

CVDLink targets federated collaborations in cardiovascular research and related biomedical domains, enabling partners to participate in secure, distributed workflows without sharing raw data.

> **Important:**  
> CVDLink is **not a replacement or independent fork** of FeatureCloud.  
> It is an **extension and specialization** built on top of the FeatureCloud engine.

---

## Relationship to FeatureCloud

CVDLink is based on the FeatureCloud platform and reuses:

- FeatureCloud controller and execution engine
- FeatureCloud app and state model
- FeatureCloud CLI command structure
- FeatureCloud testing and workflow system

CVDLink extends FeatureCloud by providing:

- A **CVDLink-specific CLI entry point**
- **Profile-based configuration** for CVDLink deployments
- **CVDLink-specific defaults** for:
  - Controller images
  - Global API endpoints
  - Docker registries
  - Relay servers
- Seamless switching between FeatureCloud and CVDLink environments using the same codebase

For general FeatureCloud concepts, architecture, and app development, please refer to:
- https://featurecloud.ai
- [FeatureCloud GitHub repositor](https://github.com/FeatureCloud/FeatureCloud/tree/cvdlink) 
- Matschinske, J., Späth, J., Bakhtiari, M., Probul, N., Kazemi Majdabadi, M. M., Nasirigerdeh, R., ... & Baumbach, J. (2023). The FeatureCloud platform for federated learning in biomedicine: unified approach. Journal of Medical Internet Research, 25, e42621.

---

## Installation

Install the CVDLink Python package via pip:

```bash
pip install cvdlink
```


## CLI Overview

CVDLink provides a **FeatureCloud-compatible command-line interface** with a dedicated entry point:

```bash
cvdlink --help
```

The CLI mirrors the FeatureCloud command structure, ensuring that existing FeatureCloud users can work with CVDLink without a learning curve.

Internally, the CLI uses a profile-based configuration, allowing the same codebase to support both FeatureCloud and CVDLink deployments.

### Controller Commands

The controller command group is used to start, manage, and inspect CVDLink controller instances.

##### Start a Controller
```bash
cvdlink controller start [NAME] [OPTIONS]
```

By default, this command:

* Uses CVDLink-specific controller Docker images
* Connects to CVDLink global API endpoints
* Uses the CVDLink relay infrastructure
* Applies CVDLink defaults defined in the configuration profile

#### Common Options

* --port: Port number for the controller (default: 8000)
* --data-dir: Directory used to store controller data
* --controller-image: Override the controller Docker image
* --global-endpoint: Override the global API endpoint
* --registry: Override the Docker registry
* --relay-address: Override the relay server address
* --poll-interval: Override workflow poll interval
* --query-interval: Override workflow query interval
* --config-file: Path to a custom configuration file inside the container

Example:
```bash
cvdlink controller start --data-dir ./data
```


Other Controller Commands

* cvdlink controller status – Display controller status
* cvdlink controller logs – Show controller logs
* cvdlink controller tail – Follow controller logs
* cvdlink controller ls – List running controllers
* cvdlink controller stop – Stop a controller instance

#### App Commands

The app command group is used to create, build, manage, and publish federated apps.

##### Create a New App
```bash
cvdlink app new --template-name <TEMPLATE_URL>
```

Creates a new federated app based on a FeatureCloud-compatible template.

Build an App Image
```bash
cvdlink app build --path <APP_PATH> --image-name <NAME> --tag <TAG>
```

Publish an App
```bash
cvdlink app publish --name <NAME> --tag <TAG>
```

Pushes the app image to the configured Docker registry. The image name should include fc.cvdlink-project.eu/ as the registry prefix which by default, this uses the CVDLink registry, unless overridden.

Additional App Commands:

* download – Download an app image
* remove – Remove a local app image
* plot-states – Visualize app states and transitions
* All app commands follow the same semantics as FeatureCloud but operate within the CVDLink ecosystem by default.