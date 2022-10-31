# FeatureCloud
<p align="center">
<img src="https://featurecloud.ai/assets/fc_logo_small.svg" width="400" height="400"/>
</p>

[FeatureCloud](https://featurecloud.eu/) provides a privacy-preserving platform for federated learning and data analysis.
Two major target groups who can benefit from FeatureCloud are researchers and developers. Any end-user who has data and 
wants to join others in a federated collaboration can use FeatureCloud without worrying about privacy concerns.
Moreover, developers can quickly implement a federated app and publish it in the [FeatureCloud App Store](https://featurecloud.ai/ai-store).
Using the [FeatureCloud engine](https://github.com/FeatureCloud/FeatureCloud/tree/master/FeatureCloud/app), developers can extend states to introduce new ones. For more information on FeatureCloud app development, please visit our [GitHub repository](https://github.com/FeatureCloud/app-template). To register and test your apps or to use apps published by others, please visit
[FeatureCloud.ai](https://featurecloud.ai/). For more information about FeatureCloud architecture,
please refer to 
[The FeatureCloud AI Store for Federated Learning in Biomedicine and Beyond](https://arxiv.org/abs/2105.05734) [[1]](#1).

## Install FeatureCloud
```shell
pip install featurecloud
```

## api
FC api includes the necessary implementation to create an app,  run, and manage the controller. It also includes the CLI to 
support command-line management of the controller.
### cli
A CLI for FeatureCloud to run the FC testing environment directly via the command-line.
#### controller
Commands to run or stop the FC controller:
* logs: Display the logs for the controller instance
  * tail: View the tail of controller logs.
  * log-level: Log level filter.
* ls: List all running controller instances
* start: Start a controller instance
  * port: Controller port number. 
  * data-dir: Controller data directory.
* status: Display general status of the controller
* stop: Stop controller instance
#### app
Basic commands to interact with FC controller regarding the app creation: 
* build: Build a docker image for the app
  * path: Path to the directory containing the Dockerfile.
  * image_name: Image name
  * tag: Image tag
  * rm: (BOOL) If True, remove intermediate containers.
* download: Download a given docker image from the FeatureCloud.ai docker repository
  * name: Image name
  * tag: Image tag
* new: Create a new app in a specific directory
  * template-name:  URL of a specific sample app provided on the FC GitHub repository. 
* plot-states: Plot app states and transitions using state names and transition labels (or names). By default, the main is used to access registered states. Alternatively, one can provide a list of .py files containing registered states. 
  * path: Path to the app directory.
  * states: Comma-separated list of `.py` files containing the states (in case of not using the main file).
  * package: Comma-separated list of sub-packages containing states (in case of not using the main file).
  * plot_name: The name of the output PNG plot file. 
* publish: Push the docker image to the FC docker repository (FC AI Store)
  * name: Image name
  * tag: Image tag
* remove: Delete the docker image from the local hard drive
  * name: Image name
#### test 
Commands to test app (or workflow of apps) execution:
* delete: Delete a single test run or all test runs
  * controller-host: Address of the running controller instance.
  * test-id: The test id of the test to be deleted. To delete all tests, omit this option and use "delete all". [required]
* info: Get details about a single test run
  * controller-host: Address of the running controller instance.
  * test-id: The test id of the test. [required]
  * format: Format of the test info (JSON or dataframe).
* list: List all test runs
  * controller-host: Address of the running controller instance.
  * format: Format of the test info (JSON or dataframe).
* logs: Get the logs of a single test run
  * controller-host: Address of the running controller instance.
  * test-id: The test id of the test. [required]
  * instance-id: The instance id of the client. [required]
  * format: Format of the test info (JSON or dataframe).
* start: Start a single test run
  * controller-host: Address of the running controller instance. 
  * client-dirs: Comma-separated client directories. 
  * generic-dir: Generic directory available for all clients. Content will be copied to the input folder of all instances. 
  * app-image: The repository URL of the app image. [required]
  * channel: The communication channel to be used. It can be `local` or `internet`. 
  * query-interval: (INTEGER) The interval (in seconds) after how many seconds the status call will be performed. 
  * download-results: (TEXT) A directory name where to download results. This will be created into the `/data/tests` directory.
* stop: Stop a single test run
  * controller-host: Address of the running controller instance. 
  * test-id: The test id of the test to be stopped. [required]
* traffic: Show the traffic of a single test run
  * controller-host: Address of the running controller instance. 
  * test-id: The test id of the test. [required]
  * format: Format of the test traffic (JSON or dataframe). 
* workflow: Subcommands to manage running a test workflow
  * controller-host: Address of the running controller instance. [required]
  * wf-dir: Path to the directory containing the workflow. [required]
  * wf-file: Python `.py` file including the workflow. [required]
  * channel: The communication channel to be used. It can be `local` or `internet`. [required]
  * query-interval: (INTEGER) The interval (in seconds) after how many seconds the status call will be performed. [required]
### imp
HTTP request commands to interact with the FC controller.
## app
The engine package in FeatureCloud introduces two major elements of app development: app and state. The app class is responsible for registering states and transitions between them, verifying the app logic, and executing them. The app is a highly transparent component 
that requires minimal developer knowledge. The second class, state, is where local computations carry on. Developers should 
insert their logic into states by assigning roles, adding and taking transitions. For more information, please refer to our 
[app-template](https://github.com/FeatureCloud/FeatureCloud/tree/master/FeatureCloud/app) repository.
## workflow
Implementing flexible non-linear workflows in the FeatureCloud platform. For more information, please refer to our 
[workflow](https://github.com/FeatureCloud/FeatureCloud/tree/master/FeatureCloud/workflow) repository.


### References
<a id="1">[1]</a> 
Matschinske, J., Späth, J., Nasirigerdeh, R., Torkzadehmahani, R., Hartebrodt, A., Orbán, B., Fejér, S., Zolotareva,
O., Bakhtiari, M., Bihari, B. and Bloice, M., 2021.
The FeatureCloud AI Store for Federated Learning in Biomedicine and Beyond. arXiv preprint arXiv:2105.05734.
