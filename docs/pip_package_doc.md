# FeatureCloud CLI
This pip package offers a CLI that is intended to be used with the `FeatureCloud <https://featurecloud.ai/>`_ 
privacy-preserving platform for federated learning and data-analysis.
Its purpose is to speed up app development of FeatureCloud apps by providing a
CLI tool for common operations related to development as well as providing a 
library for all necessary communication in federated learning.
## Install
```shell
pip install featurecloud
```
## Commands
### controller
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
### app
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
### test 
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
