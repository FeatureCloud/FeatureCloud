# FeatureCloud Example Apps

### Predefined apps in FeatureCloud platform

For the purpose of exemplifying and providing FeatureCloud users with apps
that cover preliminary operations in FC workflow, `FeatureCloud.apps` package 
contains followings apps:
- Blank
- Dice
- Round
- Library

## Developing Apps using FeatureCloud library 
In general, for developing apps in FeatureCloud platform, apps should be able to communicate with FeatureCloud controller.
For this purpose, app-developers have multiple options, that all includes employing `FeatureCloud.engine` package which 
provides the basic means. In the most simplistic way, they can extend `FeatureCloud.engine.app.State` class to define new 
custom states, and use `app_state` handler to register their state inside the app. Beware that all apps only use the default 
instance of `FeatureCloud.engine.app.App`, which is `FeatureCloud.engine.app.app`, for registering their custom states.
FeatureCloud apps can support different states and various communications; moreover, they can be used inside 
a workflow in conjunction with other apps. Inside each workflow, every app gets the input files from output of previous
app in the workflow, except for the fist one, which gets data from end-users. Accordingly, there can be a convention that 
facilitate providing acceptable results for other accompanying apps in a workflow. Therefore, we introduce a convention
that increases the readability and facilitates debugging. In the followings, we elaborate
different parts that should be included in FeatureCloud apps and how we are going to handle them.

### Defining a custom app
App states can be defined in any place, but conventionally, we recommend including all the state definition in a specific file.
Each app will be run inside a docker container, and for making the container, developers need to provide app-specific files. 

### App name
For building the app docker image and running it in FeatureCloud platform, each app should have a name, and we recommend following 
convention for it:
- app name is case-sensitive, and we recommend to use lower-cases. 
- app name should include no `space` character and better to use `_` as delimiter.
Also,this name will appear as the main key in `config.yml` file.

### Config file
Each app has some input hyper-parameters that brings some flexibility to end-users for executing it on different data or settings.
Such parameters should be included in a config file conventionally named `config.yml`. To inform end-users about the hyper-parameters
and corresponding value options, app-developers could conventionally define `default_config` dictionary witch includes the name 
of app as the only key, which includes a nested dictionary for parameters. Alternatively, this dictionary can be written
into the config file directly. Beware that once apps are used ine the workflow,
all config files, for all apps in the workflow, should be included inside same `config.yml` file and passed from one app
to the next one. So, to distinguish between app configs, we use their name. 

```angular2html
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
In this example there are `local_dataset` and `result` dictionaries, which can be necessary for almost all apps, while includes
app specific details. For instance, `task`, `target_values`, and `sep` are the options of input file, which means the data
will be related to which task, where the target_value can be found inside the file, and what is the delimiter character in
the CSV file, respectively. Alternatively, developers can directly provide the `config.yml` file with same content as follows:
```angular2html
example_app:
  local_dataset:
    data: data.csv
    task: classification
    target_value: label
    sep: ','
  result:
    data: data.csv
```
Currently, developers should explain the datatype of config options and acceptable values in their app documentation, and also,
check the values while they process the config file. Even though each config file could include arbitrary
key/value pairs, there are  share parts can be found in all apps. Here we cover how conventionally we can cover those parts.

#### Local Datasets
Each app receives some local data from clients that should be in same extension and, to some degree, in a specific format.
Currently, all input data, in different clients, should have same name and extension. Therefore, conventionally we define 
`local_dataset` as a dictionary that contains each data part required by the app and its corresponding file in clients local 
space.

#### Result
All or parts of results of an app can be used by another one in a workflow, and it should be in specific acceptable format 
the next app. Therefore, `result` is another dictionary in config file to define the expected output file name and extension.
Keys are indicating the output, which helps current app to know what should be exact name of output.

#### SMPC
SMPC module can be used in discretion of app developers to straighten user-privacy. In FeatureCloud platform,
to provides reasonable flexibility, app-developers can delegate the decision about usage of SMPC, and also, it's parameters,
to the end-users. In that case, config file could also include `use_smpc` key with boolean value to indicate the decision of
end-users. Beware that all clients, for specific communication, should have a consistent decision about using SMPC component.

#### Logic
Once the app container is built and ran, clients data will be copied inside the container, to be processed. Sometimes
there is a directory that includes multiple nested directories and/or files as input. For covering that scenarios,
conventionally, developers can include `logic` dictionary inside the config file that includes following keys:
- `mode`: value should indicate either `directory` or `file` as type of input files. Conventionally, each data that was
named in `local_dataset` can be expected as a single file or a directory including multiple splits of that single file.
A clear case of `directory` mode is CrossValidation app, which splits clients data into multiple splits.
- `dir`: The value should be either `.` that indicates the file name can be found in current directory, inside docker container, 
or name of the directory containing the input files. 


