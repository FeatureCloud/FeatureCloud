# FeatureCloud CLI
This pip package offers a CLI that is intended to be used with the [FeatureCloud](https://featurecloud.ai/) privacy-preserving platform for federated learning and data-analysis.
Its purpose is to speed up app development of FeatureCloud apps by providing a CLI tool for common operations related to development as well as providing a library for all necessary communication in federated learning.
## Install
```shell
pip install featurecloud
```
## Commands
### controller
Controller start/stop. Obtain general information about the controller.
* logs: Display the logs for the controller instance
  ```shell
  featurecloud controller logs
  ```
  * tail: View the tail of controller logs. *[optional]*
    ```shell
    featurecloud controller logs --tail=true
    ```
  * log-level: Log level filter. Will display log entries above specified level. Available log levels: info, debug, warn, error, fatal. *[optional]*
    ```shell
    featurecloud controller logs --log-level=error
    ```
* ls: List all running controller instances
  ```shell
  featurecloud controller ls
  ```
* start: Start a controller instance
  * port: Controller port number (e.g. --port=8000). *[optional]* 
  * data-dir: Controller data directory (e.g. --data-dir=./data). *[optional]*
  * gpu: Run controller with GPU access ([Read more](https://medium.com/developing-federated-applications-in-featurecloud/run-featurecloud-applications-with-gpu-acceleration-39cfec98f952)) *[optional]*
  * mount: Use this option when you want mount a folder (using absolute path) or a Docker volume that is available only to the controller's protected environment, e.g. to upload input data for apps. *[optional]*
  ```shell
  featurecloud controller start --port=8000 --data-dir=./data --gpu=true --mount=<absolute_path or volume name>
  ```
* status: Display general status of the controller
  ```shell
  featurecloud controller status
  ```
* stop: Stop controller instance
  ```shell 
  featurecloud controller stop
  ```
### app
Basic commands to interact with FC controller regarding the app creation ([Read more](https://medium.com/developing-federated-applications-in-featurecloud/create-your-first-featurecloud-app-daced512eb45)): 
* build: Build a docker image for the app
  * path: Path to the directory containing the Dockerfile. *[required]*
  * image_name: Image name *[required]*
  * tag: Image tag. *[optional]*
  * rm: (BOOL) If True, remove intermediate containers.  *[optional]*
  ```shell
  featurecloud app build ./my-app my-app:latest rm=true
  ```
* download: Download a given docker image from the FeatureCloud.ai docker repository
  * name: Image name. *[required]*
  * tag: Image tag. *[optional]*
  ```shell
  featurecloud app download featurecloud.ai/my-app:latest
  ```
* new: Create a new app in a specific directory
  * template-name:  URL of a specific sample app provided on the FC GitHub repository.*[required]*
  ```shell
  featurecloud app new --template-name=app-four my-app
  ```
* plot-states: Plot app states and transitions using state names and transition labels (or names). By default, the main is used to access registered states. Alternatively, one can provide a list of .py files containing registered states. 
  * path: Path to the app directory. *[required]*
  * states: Comma-separated list of `.py` files containing the states (in case of not using the main file). *[required]*
  * package: Comma-separated list of sub-packages containing states (in case of not using the main file). *[optional]*
  * plot_name: The name of the output PNG plot file. *[required]*
  ```shell
  featurecloud app plot-states /home/my-app mystates --states states.py --plot_name myplot
  ```
* publish: Push the docker image to the FC docker repository ([Read more](https://medium.com/developing-federated-applications-in-featurecloud/featurecloud-ai-store-publish-your-applications-2afb90c26a8d))
  * name: Image name *[required]*
  * tag: Image tag *[optional]*
  ```shell
  featurecloud app publish my-app
  ```
* remove: Delete the docker image from the local hard drive
  * name: Image name *[required]*
  * all: TAG is the image versioning tag. If set to 'all', all versions will be deleted. Default: 'latest'. *[optional]*
  ```shell
  featurecloud app remove my-app
  ```

### test 
Commands to test app (or workflow of apps) execution:
* delete: Delete a single test run or all test runs
  * controller-host: Address of the running controller instance. *[optional]*
  * test-id: The test id of the test to be deleted. To delete all tests, omit this option and use "delete all". *[required]*
  ```shell
  featurecloud test delete --test-id=1 --controller-host=http://localhost:8000
  ```
  ```shell
  featurecloud test delete all --controller-host=http://localhost:8000
  ```
* info: Get details about a single test run
  * controller-host: Address of the running controller instance. *[optional]*
  * test-id: The test id of the test. *[required]*
  * format: Format of the test info (JSON or dataframe). *[optional]*
  ```shell
   featurecloud test info --controller-host=http://localhost:8000 --format=json --test-id=1
  ```
* list: List all test runs
  * controller-host: Address of the running controller instance. *[optional]*
  * format: Format of the test info (JSON or dataframe). *[optional]*
  ```shell
  featurecloud test list --controller-host=http://localhost:8000 --format=json
  ```
* logs: Get the logs of a single test run
  * controller-host: Address of the running controller instance. *[optional]*
  * test-id: The test id of the test. *[required]*
  * instance-id: The instance id of the client. Instance id can be queried with ```featurecloud test info --test-id=<test_id>``` *[required]*
  * format: Format of the test info (JSON or dataframe). *[optional]*
  ```shell
  featurecloud test logs --controller-host=http://localhost:8000 --test-id=1 --instance-id=1 format=json
  ```
* start: Start a single test run
  * controller-host: Address of the running controller instance. *[optional]*
  * client-dirs: Comma-separated client directories. The number of clients is based on the number of directories supplied here (e.g. ```featurecloud test start --client-dirs=.,.,.,.``` command will start 4 clients). *[required]* 
  * generic-dir: Generic directory available for all clients. Content will be copied to the input folder of all instances. *[optional]* 
  * app-image: The repository URL of the app image. *[required]*
  * channel: The communication channel to be used. It can be `local` or `internet`. *[optional]*
  * query-interval: (INTEGER) The interval (in seconds) after how many seconds the status call will be performed. *[optional]* 
  * download-results: (TEXT) A directory name where to download results. This will be created into the `/data/tests` directory. *[optional]*
  ```shell
  featurecloud test start --controller-host=http://localhost:8000 --client-dirs=.,. --app-image=my-app --query-interval=1 
  ```
* stop: Stop a single test run
  * controller-host: Address of the running controller instance. *[optional]*
  * test-id: The test id of the test to be stopped. *[required]*
  ```shell 
  featurecloud test stop --controller-host=http://localhost:8000 --test-id=1
  ```
* traffic: Show the traffic of a single test run
  * controller-host: Address of the running controller instance. *[optional]*
  * test-id: The test id of the test. *[required]*
  * format: Format of the test traffic (JSON or dataframe). *[optional]*
  ```shell 
  featurecloud test traffic --controller-host=http://localhost:8000 --test-id=1 format=json
  ```
* workflow: Subcommands to manage running a test workflow. ([Read more](#test-workflow-command))
  * controller-host: Address of the running controller instance. *[required]*
  * wf-dir: Path to the directory containing the workflow. *[required]*
  * wf-file: Python `.py` file including the workflow. *[required]*
  * channel: The communication channel to be used. It can be `local` or `internet`. *[required]*
  * query-interval: (INTEGER) The interval (in seconds) after how many seconds the status call will be performed. *[required]*
  ```shell
  sudo featurecloud test workflow start --wf-dir <WORKFLOW_FILE_Path> --wf-file <NAME> --controller-host <CONTROLLER> --channel <> --query-interval <>
  ```
## Test Workflow command
Implementing flexible non-linear workflows in FeatureCloud platform

### FeatureCloud Workflow
In FeatureCloud, end-users and developers can run linear workflow in the front-end website at [https://featurecloud.ai](https://featurecloud.ai/).
They can assemble a workflow and run different apps in a linear fashion where each app will be executed after another.
Results of each app will be provided for the next one in the workflow while the results should be in the right format and extension 
which is acceptable for the upcoming app. Any workflows may involve different number of clients(data owners) who want to collaborate 
in the federated fashion, using one or more applications. Even though the online workflow serves all the needs of end-users,
developers may have challenges to flexibly employ different apps in nonlinear fashion to come-up with new solutions.
FeatureCloud developers can range from app developers who will implement federated apps that are extended version of centralized,
or the ones that are introduced originally to address federated challenges. The Latter is concerned with researchers
in various fields of science which makes it significantly trickier. In fact, developers may need arbitrary operations 
on data and results for to discover the right solution which may involve pre-/post-processing apps or operations.
Long story short, here we introduce FeatureCloud test workflow, where developers can assemble an arbitrary workflow for research purposes.
Such test workflows, are not supported in the app store, and once the developers came with final solution, they ought to 
present it as an app that may be run in conjunction of other apps in a workflow. In FC test workflow, each app will be run as 
a test app in the test-bed. Accordingly, all the functionalities are applied to the test-run that runs a specific app.

### Methods

#### Set apps test ID
`def set_id(self, test_id: int)`: Set the app's test ID and partially define the delete method based on it.

#### Extract the results (zip files)
 `def extract_results(self, def_res_file: str)`: extract app's results zip files for all clients into their corresponding directories

#### Wait for the end of app execution
`def wait_until_finishes(self)`: Waits until the app status becomes finished.

#### Check the app is finished or not
`def is_finished(self)`: Check either the app status is finished.

#### Create and remove directories
`def clean_dirs(self, def_re_dir: str)`: creates results directories. And removes existing results in the directories

#### Generate paths to data and results dirs
`def create_paths(self, ctrl_data_path: str, ctrl_test_path: str)`: Generate paths to directories containing the app's data(for each client)
And also for app's results.
```angular2html
Parameters
----------
ctrl_data_path: str
    path to the target controller's data folder
ctrl_test_path: str
    path to the target controller's tests folder
```
#### Copy final results, as data for the next app.
`def copy_results(self, ctrl_data_path: str, dest_generic: str, dest_clients: list, default_res_name: str)`:
Copy results of the app to as the data to the directory of the next app.

```angular2html
Parameters
----------
ctrl_data_path: str
    path to the target controller's data folder
dest_generic: str
    Full path to directory containing
    the generic data of the next app in the workflow
dest_clients: str
    Full path to directory containing
    the clients' data of the next app in the workflow
default_res_name: str
    Default name for the app's result directory
    Same name for all clients.

```

### TestWorkFlow
The TestWorkFlow class is an abstract class that provides basic functionalities for general workflows.
It asks developers to extend it and implement run() and register_app methods.
#### Attributes
##### apps
It includes a list of instances of TestApp class as apps that should be run in the workflow.
The order of registering apps will be preserved, however, developers can run them in any arbitrary manner.
##### controller
An instance of Controller class that helps developers to have same operations for all running test-runs with different apps.
##### default_res_dir_name
It is a name for the result directory that contains all extracted results from the zip file for each client in each app.
This directory provides the data for the upcoming app. 
#### Methods
 
##### Registering an app: `def register_app(self)`
This abstract method should be implemented by developers to register apps into the workflow. The apps will be added to the `self.apps`
list and will be available in the run method to be executed.

##### Running the workflow: `def run(self)`
It is another abstract method tha should be implemented by developers to run the workflow.
Developers can implement an arbitrary flow of app execution when they have access to the data and results of each app.

##### Registering a TestApp instance `def register(self, app)`
Adding `TestApp` instance to the app list and logging the apps attributes.

##### Stopping all running apps on the WF's controller: `def stop(self)`
Stop all test-runs in the controller.
##### Deleting all the running containers in the WF: `def delete(self)`
Delete all test-runs in the controller.

##### Getting information of all running test-runs in the WF's controller: `def info(self, format: str)`
info of all tests in the specified controller or all of them.

### Tips for implementing and running workflows
For implementing a desired workflow, developers should extend `TestWorkFlow` class and implement `register_apps` and `run` methods.
The name of the extended class should always be `WorkFlow` and it asks for the controller address, channel, and query interval for querying the controller.
After implementing the workflow, developers can run it using FeatureCloud pip package:

```angular2html
sudo featurecloud test workflow start --wf-dir <WORKFLOW_FILE_Path> --wf-file <NAME> --controller-host <CONTROLLER> --channel <> --query-interval <>
```

Beware that due to the file permissions, the workflow should be run using supper-user access.
ALl the data and results will be available in the controller's data directory. In fact, data for the first app should be provided 
in `app{app_n}` folder. Where `app_n` is the index the target app in WF's `apps` list. The same numbering applies for all the registered
apps, and results will be directly moved into the next app's directory. Even though the controller write result zip
files in `tests` directory, for each app, the extracted results will be available in corresponding app folder in `data` directory.
