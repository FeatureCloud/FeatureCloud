# Developing federated apps using FeatureCloud platform

For registering and testing your apps or using other apps, please visit
[FeatureCloud.ai](https://featurecloud.ai/). And for more information about FeatureCloud architecture,
please refer to 
[The FeatureCloud AI Store for Federated Learning in Biomedicine and Beyond](https://arxiv.org/abs/2105.05734) [[1]](#1).


## Developing Apps using FeatureCloud library
FeatureCloud library facilitates app development inside the FeatureCloud platform. To develop apps, developers
should define their states and register them to the default app.

### defining new states
For defining new states, in general, developers can use [`AppState`](engine/README.md#appstate-defining-custom-states)
which supports different communications, transitions, logging, and operations.

#### AppState
[`AppState`](engine/README.md#appstate-defining-custom-states) is the building block of FeatureCloud apps that covers
all the scenarios with the verifying mechanism. Each state of 
the app should extend [`AppState`](engine/README.md#appstate-defining-custom-states), which is an abstract class with two specific abstract methods:
- [`register`](engine/README.md#registering-a-specific-transition-for-state-register_transition):
should be implemented by apps to register possible transitions between the current state to other states.
This method is part of verifying mechanism in FeatureCloud apps that ensures logically eligible roles can participate in the current state
and transition to other ones.
- [`run`](engine/README.md#executing-states-computation-run): executes all operations and calls for communication between FeatureCloud clients.
`run` is another part of the verification mechanism in FeatureCloud library, that ensures the transitions to other states are logically correct
by returning the name of the next state.


### Registering apps
For each state, developers should extend one of the abstract states and call the helper function to automatically register
the state in the default FeatureCloud app:

```python
@app_state(name='initial', role=Role.BOTH)
class ExampleState(AppState):
    def register(self):
        self.register_transition('terminal', Role.BOTH)

    def run(self):
        self.read_config()
        self.app.log(self.config)
        return 'terminal'
```

### building the app docker image
Once app implementation is done, for building the docker image for testing, or adding it to
[FeatureCloud AI store](https://featurecloud.ai/ai-store?view=store&q=&r=0),
developers should provide following files.
#### Dockerization files

For dockerizing apps, regardless of their applications, there should be some specific files:

1. [Dockerfile](Dockerfile)
2. [server-config](server_config)
   - [docker-entrypoint.sh](server_config/docker-entrypoint.sh)
   - [nginx](server_config/nginx)
   - [supervisord.conf](server_config/supervisord.conf)

In older versions of FeatureCloud one should provide a build.sh file or buildthe docker image with 
acceptable name by command like this:
```shell
docker build $PATH_TO_APP_DIR --tag $IMAGE_NAME
```
However, with FeatureCloud CLI, one can simply use [`featurecloud app build`](../../README.md#app) command conveniently.
Developers should ensure that these files with same structure and content are exist in the same directory as their app
implementation. 


#### App-specific files
All app-specific files should be included data or codes that are strictly dependent to app's functionality.

##### main.py
Each app should be implemented in a directory that includes the [`main.py`](main.py) file which in turn includes either direct
implementation of states or importing them. Moreover, `main` should import `bottle` and `api` package:
```python
from bottle import Bottle

from api.http_ctrl import api_server
from api.http_web import web_server

import apps.examples.dice

from engine.app import app

server = Bottle()
```
Here we imported `dice` app from our [`apps`](apps/README.md) package which because of putting 
[`app_state`](engine/README.md#registering-states-to-the-app-app_state) on top of state classes, 
merely importing the states register them into the [`app` instance](engine/README.md#app-instance).     

For running the app, inside a docker container, [`app.register()`](engine/README.md#registering-all-transitions-appregister)
should be called to register and verify all transitions; next, api and servers should mount at corresponding paths; and finally
server is ready to run the app.

```python
app.register()
server.mount('/api', api_server)
server.mount('/web', web_server)
server.run(host='localhost', port=5000)
```

All of aforementioned codes, except for importing the app, or alternatively, implementing states, can be exactly same for all apps.  

##### requirements.txt
for installing required python libraries inside the docker image, developers should provide a list of libraries in [requirements.txt](requirements.txt).
Some requirements are necessary for FeatureCloud library, which should always be listed, are:
```angular2html
bottle
jsonpickle
joblib
numpy
bios
pydot
pyyaml
```

And the rest should be all other app required libraries.

##### Config file: config.yml


Each app has some input hyper-parameters that brings some flexibility to end-users for executing it on different data or settings. Such parameters should be included in a config file conventionally named `config.yml`. To inform end-users about the hyper-parameters and corresponding value options, app-developers could conventionally define `default_config` dictionary witch includes the name of app as the only key, which includes a nested dictionary for parameters. Alternatively, this dictionary can be written into the config file directly. Beware that once apps are used ine the workflow, all config files, for all apps in the workflow, should be included inside same `config.yml` file and passed from one app to the next one. So, to distinguish between app configs, we use their name.
```yaml
default_config = {
    'example_app': {
        'local_dataset': {
            'data': 'data.csv'
            'task': 'classification',
            'target_value': 'label',
            'sep': ','
        }        
        'result': {
            'data': 'data.csv'
        }
    }
}
```


In this example there are `local_dataset` and `result` dictionaries, which can be necessary for almost all apps, while includes app specific details. For instance, `task`, `target_values`, and `sep` are the options of input file, which means the data will be related to which `task`, where the `target_value` can be found inside the file, and what is the delimiter character in the CSV file, respectively. Alternatively, developers can directly provide the `config.yml` file with same content as follows:
```yaml
example_app:
  local_dataset:
    data: data.csv
    task: classification
    target_value: label
    sep: ','
  result:
    data: data.csv

```

Currently, developers should explain the datatype of config options and acceptable values in their app documentation, and also, check the values while they process the config file. Even though each config file could include arbitrary key/value pairs, there are share parts can be found in all apps. Here we cover how conventionally we can cover those parts.
###### Local Datasets

Each app receives some local data from clients that should be in same extension and, to some degree, in a specific format. Currently, all input data, in different clients, should have same name and extension. Therefore, conventionally we define `local_dataset` as a dictionary that contains each data part required by the app and its corresponding file in clients local space.
###### Result

All or parts of results of an app can be used by another one in a workflow, and it should be in specific acceptable format the next app. Therefore, `result` is another dictionary in config file to define the expected output file name and extension. Keys are indicating the output, which helps current app to know what should be exact name of output.
###### SMPC

SMPC module can be used in discretion of app developers to straighten user-privacy. In FeatureCloud platform, to provides reasonable flexibility, app-developers can delegate the decision about usage of SMPC, and also, it's parameters, to the end-users. In that case, config file could also include `use_smpc` key with boolean value to indicate the decision of end-users. Beware that all clients, for specific communication, should have a consistent decision about using SMPC component.

###### Logic

Once the app container is built and ran, clients data will be copied inside the container, to be processed. Sometimes there is a directory that includes multiple nested directories and/or files as input. For covering that scenarios, conventionally, developers can include `logic` dictionary inside the config file that includes following keys:

* `mode`: value should indicate either `directory` or `file` as type of input files. Conventionally, each data that was named in `local_dataset` can be expected as a single file or a directory including multiple splits of that single file. A clear case of `directory` mode is CrossValidation app, which splits clients data into multiple splits.
* `dir`: The value should be either `.` that indicates the file name can be found in current directory, inside docker container, or name of the directory containing the input files.

### References
<a id="1">[1]</a> 
Matschinske, J., Späth, J., Nasirigerdeh, R., Torkzadehmahani, R., Hartebrodt, A., Orbán, B., Fejér, S., Zolotareva,
O., Bakhtiari, M., Bihari, B. and Bloice, M., 2021.
The FeatureCloud AI Store for Federated Learning in Biomedicine and Beyond. arXiv preprint arXiv:2105.05734.
