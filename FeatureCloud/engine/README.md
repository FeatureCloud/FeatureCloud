# FeatureCloud Engine
### Defining states and running applications

FeatureCloud provide an advantageous platform to develop Federated applications.
FeatureCloud includes different components to develop applications in a privacy-preserving fashion and present 
them to researchers and practitioners. FeatureCloud AI store includes different exciting applications developed by
FeatureCloud community, a testbed to facilitate app development for developers, and project front-end for FeatureCloud
end-users to run desired workflows containing multiple applications. For registering and testing your apps
or using other apps, please visit [FeatureCloud.ai](https://featurecloud.ai/). And for more information about
FeatureCloud architecture, please refer to our paper:
[The FeatureCloud AI Store for Federated Learning in Biomedicine and Beyond](https://arxiv.org/abs/2105.05734) [[1]](#1).


FeatureCloud library provides app developers with  `AppState` and `App` classes that are responsible for defining states and executing the app instance, respectively.
Each app, in the FeatureCloud platform includes multiple states
and possible transitions between the defined states. All apps will begin their workflow from the `initial` state
and end it at the `terminal` state. Accordingly, `App` class will manage stets and transitions registration. 
FeatureCloud `App` supports exactly two roles, coordinator and participant, for clients who are going to participate
in Federated execution of apps. FeatureCloud app developers are obliged to explicitly define their logic
for the app by stipulating which roles are allowed to enter a specific state and take a particular transition.

## Roles
In the FeatureCloud platform, clients can have two roles: coordinator and participant. These roles are not mutually exclusive.
Meanwhile, the FeatureCloud library comes with three constant tuples to describe the eligibility of clients in terms of
their role to enter and execute specific states.  Accordingly, to make it clear, we defined three role tuples, with `bool` values, 
for participant and coordinator roles, as follows: 

* `COORDINATOR`: indicates that only coordinator role is `True`. 
* `PARTICIPANT`: indicates that only participant role is `True`.
* `BOTH`: indicates that both roles are `True`.

FeatureCloud app developers can use these constants for defining roles for states and transitions. 

##  Operational States
Once states are executing, any exceptions or errors can happen that can be handled automatically by the app.
For reporting the situation for the front-end app, so end-users be aware of it, currently, three key values can be communicated to the controller:

Operational states | 'running' | 'error' | 'action_required' 
--- | --- | --- | --- |
Constants | RUNNING | ERROR | ACTION | 
Interpretation | the app is functioning normally |  app execution is interrupted with an error and cannot recover from it | demands end-users ’ intervention in interactive apps|
 
FeatureCloud app developers can use these pre-defined values for updating the front-end for end-users.

## Log levels
For proper logging and observing them in the front-end, there is a constant `LogLevel` enumerator that includes the following levels:
- `DEBUG`: should be used once developers want to show some debug-related logs. 
- `ERROR`: Once the app catches some errors, this log-level helps to properly message the error in the front-end while app execution will be terminated by raising `ValueError`.
`FATAL`: Like `ERROR`, it can be used to log fatal events that the app may encounter during the execution.


## Secure Multi-Party Computation (SMPC)
Despite privacy-awareness in Federated Learning, not sending around raw data, there are a couple of steps
to strengthen privacy issues. In that regard, FeatureCloud provides Secure Multi-Party Computation (SMPC) 
module for aggregating clients' data. In the SMPC component, you can include all or at least two of clients as Computational
Parties (CP). Those parties will receive exclusively either noisy data or noises from clients. No CP will receive both
noise and noisy data parts from the same client. The amount of noise that should be used to make data noisy can be tricky.
On one side, excessive noise can damage the results, and on the other hand, slight noises can compromise privacy.
After getting noisy data and/or noises, each CP sums up the data and moves the results to the coordinator.
Finally, the coordinator will conclude the aggregation phase.
SMPC component is part of FeatureCloud Controller, and we encourage developers to have a basic understanding of its application
to provide the controller with proper SMPC configuration. For more information about the SMPc module, please visit [FeatureCloud.ai](https://featurecloud.ai/)
or refer to our [paper](https://arxiv.org/abs/2105.05734) [[1]](#1).

```angular2html
class SMPCType(TypedDict):
    operation: Literal['add', 'multiply']
    serialization: Literal['json']
    shards: int
    exponent: int
```
### Exponent
By randomly drawing a noise value, we generate the noise for
making the data noisy. Regarding the fact that noise values cannot
be zero or negative, the Exponent should be a non-negative integer where zero practically means not using the SMPC component.

### Shards
Each client should send out noise and noisy data to Computational Parties (CP), between two and the number of clients. 
Noise can be made of one or more secrete values, and clients should generate those secrete random values regarding the
number of shards. For instance, once the shards are two, clients should send out one secrete value, 
and noisy data, of course, to different CPs. For three or more shards, more secrete values should be generated.
Even though the maximum number of parties yields the best privacy-preserving results, 
it is computationally expensive. Accordingly, `shards` is a non-negative integer, where choices are:
- `0`: Maximum number of computational parties(Number of clients)
- `1`: Practically, the SMPS module will not be used.
- `Values greater than one`: indicates the number of Computational parties that will be involved.
  For values greater than the number of clients, all clients will be involved as CPs. 
 
### Operations
For employing noise to the clients' data, we can use different operations. Currently, FeatureCloud supports 
two of the most common operations to make noisy data: add and multiply. App-developers can choose between 
these two options, by providing the string value of `add` or `multiply`, or simply to avoid typos, they can 
use following constants:
```angular2html
OPERATION_ADD = 'add'
OPERATION_MULTIPLY = 'multiply'
```

### Serialization
To communicate data between clients and the aggregated results of the SMPC module to the coordinator, we should use serialization.
For serialization technique, FeatureCloud library currently supports `json` and `pickle` libraries. For communicating 
data to the SMPC component and from SMPc to the coordinator, we use `json`, which only accepts Python list, dictionary, and tuple.
We use `pickle` for all other communications, supporting more complicated structures like Pandas Dataframes and Series and NumPy arrays.

## App class
`App` class is the central part of the FeatureCloud engine responsible for registering states, transit between states, and managing their state executions,
in general. Developers do not need to be familiar with `App` class; however, they should be aware of some principles that developers should follow.

Generally, two types of clients are used in FeatureCloud:

- participant: Every participant in the FeatureCloud platform, except for one, the coordinator,
  is considered a participant who should perform local tasks and communicate some intermediary results with the coordinator.
  Of course, no raw data are supposed to be exchanged among clients and the coordinator.
- coordinator: One of the clients who can receive results of other clients, aggregate, and broadcast them.


For registering either states or transitions, app developers must use one of these constants
to declare that each role/s are responsible/allowed to execute states or take transitions. `App` class
automatically checks the logic to ensure semantic errors in defining the workflow are minimized.

Each app should contain and start with an `initial` state. On the other hand, each app, by default, contains 
the `terminal` state that has no task or operation to accomplish other than explicitly
marking the final state in the app. Once a state transitions to the `terminal` state, that state should be considered one of the app's possible exit states.


### Status Attributes
When the app instance is running, different errors may happen, or various results may be produced. Thereby, the app instance may need
to communicate with the controller or front-end parts of FeatureCloud. Accordingly, developers can use status 
attributes in the `App` class to send messages between the app container to the controller and/or indirectly with the front-end.
Beware that app containers are not directly connected to the front-end, and they should communicate through the controller.

#### Availability of data to communicate: `app.status_available`
Once a client wants to communicate with other clients, regardless of role, and the data is ready, by setting 
`app.status_available` as `True`, the app instance sends the signal to the controller to execute the communication. Generally, this attribute will be used for [communication methods](#communication-methods) and automatically handled by the FeatureCloud app.

#### Termination of app execution: `app.status_finished
The app instance can set `app.status_finished` attribute as `True` to signal the controller that app execution is finished.
Generally, this attribute will be set as True by the FeatureCloud app once the app enters the `terminal` state or some
exceptions happen during the app run. 

#### Messaging to the Front-end: `app.status_message`
Once there is a specific massage, e.g., the occurrence of some semantic errors, app instance can use `app.status_message`
to inform the end-user in front-end.  For sending messages to front-end, developers can use [`app.update`](#updating-local-app-status-update).

#### Overall progress of app: `app.status_progress`
During the run, app execution progress can be quantified based on different factors. Developers can quantify the app
progress in the range of zero to one and share it with end-user through the front-end using [`app.update`](#updating-local-app-status-update).

#### Operational state of the app: `app.status_state`
During the app run, different [operational states](#operational-states) can be reported to the end-user using [`app.update`](#updating-local-app-status-update).

#### Messaging to other clients: `status_destination`
Once clients want to communicate with another client, they should provide the ID of the target client for the coordinator.
Developers should use `destination` argument in [communication methods](#communication-methods) for this purpose and `status_destination`
will be accordingly and automatically handled by app instance.

#### Desired configuration of SMPC component: `app.status_smpc`
App developers can decide which parameters should be used SMPC aggregation, and they can inform the controller about the 
aconfiguraion using [`app.configure_smpc`](#configuring-smpc-module-configure_smpc).

### Shared memory for states: `app.internal`
Different states can be defined and registered to the app, and they may need to pass data to each other. To support a shared memory
between different states, `App` class has `internal` attribute, which is a dictionary that can be accessed through 
`self.app.iternal` in each state.

### Registration methods
The FeatureCloud app includes various methods that not only provides 
the ability to flexibly incorporate different states into the app but also work as part of the [verification mechanism](#verification-mechanism).

#### Registering all transitions: `app.register()`
Once all the states are registered and ready to run, `app.register()` should be called to register all the transitions. 
This is one part of [Verification mechanism](#verification-mechanism). 

#### Registering a state: `_register_state(self, name, state, participant, coordinator, **kwargs)`
Once the state is submitted by calling [app_state](#registering-states-to-the-app-app_state), `_register_state` will be
automatically called to instantiate the state class and assign the roles and name. Generally, developers should extend 
`AppState` and implement abstract classes; the defined state may have arguments that can be passed to using `**kwargs`. 
+ name: name of the state(which will be used in logging and creating transitions)
+ state: AppState class or any extensions of it.
+ participant: a boolean flag that indicates whether participants are allowed to enter the state or not.  
+ coordinator: a boolean flag that indicates whether the coordinator is allowed to enter the state or not.

#### Registering a transition: `register_transition(self, name, source, target, participant, coordinator)`
It has a similar application as `_register_state` except it registers states. It receives the names of source and 
target states and registers a transition between them. Meanwhile, it checks the logic and raises `RuntimeError` if apps try to register a
transitions with contradicting roles.

### Execution methods
During the run, app instances need to transition between different states, execute them and provide logs.

#### Transition to another state: `transition(self, name)`
Transits the app workflow to the next state based on current states, the role FeatureCloud client,
and requirements of registered transitions for the current state. For transition to a specific state, this method needs the
target state's name and considers the current state as the source state.

#### Executing state's computation: `run`
The main method in `App` class runs the workflow while logging the current state execution
and transits to the next desired state. Meanwhile, once the app transits to the finish state,
the workflow will be terminated.

#### Logging: `app.log(msg, level)`
Prints a log message or raises an exception according to the [log level](#log-levels).

## AppState: Defining Custom States
To Support all sorts of operations and communications, FeatureCloud's engine package includes `AppState` 
class. It is an abstract class that requires App-developers to extend it by defining its [abstract methods](#abstract-methods).
Sates will be assigned to clients with specific roles, and the FeatureCloud app will verify all states and their
corresponding transitions based on these predefined roles. In this way, 
the app's logic can be verified before deploying it(more on this [here](#verification-mechanism)). Each state
should have a unique name that, by default, will be used for naming transitions. Also, for roles, developers
should set `participant` and `coordinator` attributes(which we strongly recommend to use [`app_state`](#registering-states-to-the-app-app_state) handler).  
Also, for each state, the app instance should be assigned, so states can have access to the app's attributes,
especially `internal` attribute that should be used as a shared memory between all states.

`AppState` includes generic methods for sending data around that all use `json` serialization when using SMPC and `pickle` for other communications. 
To provide a more secure way of communicating data, FeatureCloud incorporates Secure Multi-Party Computation (SMPC), 
and regarding using it or not, different serialization methods will be used:

- `json`: will be used once we do not use SMPC for aggregation and can handle Numpy arrays and Panda DataFrames and Series.
- `pickle`: will be used once SMPC is used for aggregation and only supports Python lists, tuples, and dictionaries.

Therefore, app developers should consider data type and structure when they communicate data that should be aggregated.
The data may not be in the same structure or type as they were sent out.

### Abstract methods
For developing apps in FeatureCloud, developers need to extend `AppState` class to define their states. And for
implementing new states, developers are only required to implement two abstract methods, `register` and `run`, which are responsible
to register transitions and execute local computations, respectively.

#### Registering transitions: `register(self)`
Developers should implement this method to register all possible transitions. To do so, developers should call
`self.register_transition(target, role, name)`, where they should provide the name of target transition and other parameters.
Beware that this is just a declaration of transitions and later in [`app._transition`](#transition-to-another-state-transitionself-name)
eligibility of the transition will be checked. Accordingly, there is no need to check the app-instance role here.
This method will be called in `app.register` method to verify all transitions.

#### Executing local computations: `run(self)`
All the operations that should be executed as either local calculations or global aggregations should be implemented in the `run` method.
Depending on the roles, in case both roles are allowed, there can be a different set of operations to handle.
Meanwhile, developers should call the communication methods, in case it is needed, to communicate. 
It will be called in [`app.run()`](#executing-states-computation-run) method so that the state perform its operations.




### Communication methods
Generally, each state can communicate with other clients through different communication methods.

#### Aggregating clients data: `aggregate_data` 
This method automatically handles SMPC usage and serialization and always returns the aggregated data. Aggregated data 
contains the same data structure and shape as the one was sent out by each of the clients because it was summed up element-wise. Therefore,
to have structural data consistency, it considers SMPC usage as follows:
- Using SMPC: waits to receive the aggregated data from SMPC modules, it looks like waiting for just one client.
- Without SMPC: waits to receive all client's data, then internally aggregates them.

Accordingly, FeatureCloud app developers no longer are required to consider SMPC usage because they always get the same
aggregated results in the coordinator. Provided aggregated results are not the average ones; therefore, they need to be averaged, if it's apt to, separately.

#### Gathering clients data: `gather_data`
FC app developers are allowed to call this method only for clients with the coordinator role.
This method calls the `await_data` method to wait for receiving data of all clients.            

#### Waiting to receive data: `await_data`
For receiving data from `n` clients, it can be called. It polls for data arrival every `DATA_POLL_INTERVAL` seconds, 
and once it is received, deserializes the received data.  

#### Communicating Data to others: `send_data_to_participant`
Once it is called, it communicates data to another specific client that was named by its `id`.

#### Configuring SMPC Module `configure_smpc`
 Developers can configure the Secure Multi-Party Computation(SMPC) module by sending range, shards,
 operation, and serialization parameters. In case of not calling the method, default configurations will be used
 (More information on [here](#secure-multi-party-computation-smpc)).

#### Communicating data to the coordinator: `send_data_to_coordinator`
Developers can use `send_data_to_coordinator` this method to Communicate data with the coordinator. 
It provides the data for the FC Controller to be delivered to the coordinator. And if the coordinator calls it,
data will be directly appended to its list of incoming data. Developers should decide whether they want
to employ SMPC for securing the aggregation or not by setting `use_smpc` flag.

#### Broadcasting data: `broadcast_data`
This should only be called for the coordinator to broadcasts data to all clients.

### Other methods 

#### Registering a specific transition for state: `register_transition`
Developers should call this method to register a transition for the state by determining the name of
`target` state, `role` tuple of transitions, and a postfix name for generating the name of the transition.
In case of not providing the postfix, the name of the target state will be used. For naming the transitions,
we conventionally use `name of source state`_`name of target state`. In `AppState.register`, `register_transition` of the states
will be called to verify and add all possible transitions.

#### Updating local app status: `update`
Updates the status of the instance app for the front-end application. It can be called by any of the clients to report the client's state.
- message: messaging any specifics about state or app. 
- progress: quantifies the approximate progress of the application. 
- state: message that describes actual/general state of the app.


## Registering states to the app: `app_state`
Once FC app developers want to integrate their newly defined states, they can use `app_state`. FeatureCloud app
will always be instantiated in the `FeatureCloud.engine` package to be used by different modules. Each state should be
defined for at least one participant or coordinator role. In case states require any specific arguments, they should be sent by the `app_state` function.
For instance, to register the `initial` state with the constant role of `BOTH` and `app_name` as a state-specific argument,
we can use `app_state` as follows:

```angular2html
@app_state(name='initial', role=BOTH, app_name=name)
class ExampleState(State):
    def __init__(app_name)
```
This will automatically register `ExampleState` as the first state by the name of `initial` in the app. Meanwhile, once the state is instantiated, `app_name` will be passed to it.

## Verification mechanism
To verify the logic of defined states and transitions between them, FeatureCloud use a verification mechanism that operates 
in two levels. In step level: 
in app level, ever

## app instance
Different parts of the FeatureCloud library should use the same instance of the `App` class. These parts are as follows:
- States: each state may need to be aware of the [Role](#roles) for carrying on different operations and have access to the app's 
[`internal`](#shared-memory-for-states-appinternal) for data from other states. Therefore, the same app instance should be used for registering the states.
- api: In the `api` package, through the `bottle` library, the controller informs the app instance about its role, its ID, and ID of other
clients. The same app instance should be used for that purpose too.


### References
<a id="1">[1]</a> 
Matschinske, J., Späth, J., Nasirigerdeh, R., Torkzadehmahani, R., Hartebrodt, A., Orbán, B., Fejér, S., Zolotareva, O., Bakhtiari, M., Bihari, B. and Bloice, M., 2021. The FeatureCloud AI Store for Federated Learning in Biomedicine and Beyond. arXiv preprint arXiv:2105.05734.
