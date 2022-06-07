# FeatureCloud
<p align="center">
<img src="https://featurecloud.ai/assets/fc_logo_small.svg" width="400" height="400"/>
</p>

[FeatureCloud](https://featurecloud.eu/) provides a privacy-preserving platform for federated learning and data analysis.
Two major target groups who can benefit from FeatureCloud are researchers and developers. Any end-user who have data and 
want to join others in a federated collaboration can use FeatureCloud without worrying about privacy concerns.
On the other hand, developers can quickly implement a federated app and publish it in [FeatureCloud AI-store](https://featurecloud.ai/ai-store).
Using [FeatureCloud engine](https://github.com/FeatureCloud/FeatureCloud/tree/master/FeatureCloud/app), developers can extend states to introduce new ones; for more information on developing apps, you can visit our [GitHub repository](https://github.com/FeatureCloud/app-template). For registering and testing your apps or using other apps, please visit
[FeatureCloud.ai](https://featurecloud.ai/). And for more information about FeatureCloud architecture,
please refer to 
[The FeatureCloud AI Store for Federated Learning in Biomedicine and Beyond](https://arxiv.org/abs/2105.05734) [[1]](#1).

## Install FeatureCloud
```shell
pip install featurecloud
```

## api
FC api includes the necessary implementation to creat an app, run and manage the controller. It also includes the CLI to 
support commandline management of controller.
### cli
A CLI for FeatureCloud to run the FC testing environment directly via the command-line.
#### controller
Commands to run or stop the FC controller:
* logs: Display the logs for the controller instance
  * tail: View the tail of controller logs.
  * log-level: Log level filter.
* ls: Lists all running controller instances
* start: Start controller
  * port: Controller port number. 
  * data-dir: Controller data directory.
* status: Display general status of the controller
* stop: Stop controller instance
#### app
Basic commands to interact with FC controller regarding the creating apps and
* new: to create a new app in a specific directory
  * template-name:  URL of a specific sample app provided on FC GitHub repositories 
* build: to build docker image for the app
  * path: to the directory containing the Dockerfile
  * image_name
  * tag
  * rm: (bool) if True, remove intermediate containers
* publish: to push the docker image to the FC docker repository(FC AI-store)
  * name: image name
  * tag
* Download a given docker image from FeatureCloud.ai docker repo.
  * name: image name
  * tag
* remove: Delete docker image from local hard drive.
  * name: image name

#### test 
Commands to manage app(or test workflow of apps) execution:
* delete: Delete a single test run or all test runs
  * controller-host: Address of your running controller instance.[required]
  * test-id The test id of the test to be deleted. To delete all tests omit this option and use "delete all".
* info: Get details about a single test run
  * controller-host: Address of your running controller instance.[required]
  * test-id The test id of the test to be deleted. To delete all tests omit this option and use "delete all".
  * format: Format of the test info. json or dataframe [required]
* list: List all test runs
  * controller-host: Address of your running controller instance.[required]
  * format: Format of the test info. json or dataframe [required]
* logs: Get the logs of a single test runs
  * controller-host: Address of your running controller instance.[required]
  * test-id The test id of the test to be deleted. To delete all tests omit this option and use "delete all".
  * instance-id: The instance id of the client.  [required]
  * format: Format of the test info. json or dataframe [required]
* start: Start a single test run
  * controller-host: Address of your running controller instance.[required]
  * client-dirs: Client directories seperated by comma.  [required]
  * generic-dir: Generic directory available for all clients.Content will be copied to the input folder of all instances.  [required]
  * app-image: The repository url of the app image.  [required]
  * channel: The communication channel to be used. Can be local or internet.  [required]
  * query-interval INTEGER  The interval after how many seconds the status call will be performed.  [required]
  * download-results TEXT   A directory name where to download results. This will be created into /data/tests directory
* stop: Stop a single test run
  * controller-host: Address of your running controller instance. [required]
  * test-id: The test id of the test to be stopped.
* traffic: Show the traffic of a single test run
  * controller-host: Address of your running controller instance.[required]
  * test-id: The test id of the test to be stopped.
  * format: Format of the test traffic. json or dataframe[required]
* workflow: Subcommands to manage running a test workflow
  * controller-host: Address of your running controller instance.[required]
  * wf-dir: path to directory containing the workflow[required]
  * wf-file: python file including the workflow  [required]
  * channel: The communication channel to be used. Can be local or internet.  [required]
  * query-interval: The interval(in seconds) after how many seconds the status call will be performed.  [required]
### imp
HTTP request commands to interact with the FC controller.
## app
The engine package in FeatureCloud introduces two major elements of app development: app and state. App class is responsible for registering states and transitions between them, verifying the app logic, and executing them. The app is a highly transparent component 
that requires minimum developers' familiarity. The second class, state, is where local computations carry on. Developers should 
insert their logic into states by assigning roles, adding, and taking transitions. For more information please refer to our 
[app-template](https://github.com/FeatureCloud/FeatureCloud/tree/master/FeatureCloud/app) repository.
## workflow
Implementing flexible non-linear workflows in FeatureCloud platform. For more information, please refer to our 
[Wrokflow](https://github.com/FeatureCloud/FeatureCloud/tree/master/FeatureCloud/workflow) repository.


### References
<a id="1">[1]</a> 
Matschinske, J., Späth, J., Nasirigerdeh, R., Torkzadehmahani, R., Hartebrodt, A., Orbán, B., Fejér, S., Zolotareva,
O., Bakhtiari, M., Bihari, B. and Bloice, M., 2021.
The FeatureCloud AI Store for Federated Learning in Biomedicine and Beyond. arXiv preprint arXiv:2105.05734.
