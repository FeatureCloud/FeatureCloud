===============
Getting Started
===============

The FeatureCloud CLI
--------------------
The FeatureCloud CLI tool is available as a pip package.

Prerequisites
^^^^^^^^^^^^^
- `Docker <https://www.docker.com/>`_ needs to be installed
- `Python <https://www.python.org/>`_ needs to be installed

Installation
^^^^^^^^^^^^
``pip install featurecloud``

Usage
^^^^^

Main commands of the CLI
^^^^^^^^^^^^^^^^^^^^^^^^

========================= ========================= =========================
Command                   Description               Subcommands
========================= ========================= =========================
**controller**            Controller start/stop     help, logs, ls, start, status, stop
**app**                   App related commands      help, build, download, new, plot-states, publish, remove
**test**                  Testbed related commands  help, delete, info, list, logs, start, stop, traffic, workflow
========================= ========================= =========================

More details about commands and its subcommands are available `here <./pip_package_doc.html>`_


Application development
-----------------------
There are two ways to implement applications for FeatureCloud:

- :ref:`App template based development (recommended) <app temp anchor>`
- :ref:`Developing applications from scratch <dev from scratch anchor>`

Both ways rely (and relay) on the so called *controller*. The controller is a dockerized
server responsible for the communication. The featurecloud pip package offers
functioanlity to communicate with the controller.

To test applications in development, the *test* functioanlity of the CLI can be
used.

.. _app temp anchor:

App template based development (recommended)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Create a directory with the wanted template (:ref:`templates <app templates>`)

``featurecloud app new --template-name=app-blank my-app``

1. Implement your own application using the template
    * *Implementation of the app logic:* The implementation itself happens in `states.py`. 
      
      * You may use (and we recommended using) *states*.  Any state must have the 
        ``@app_state('[statename]')`` decorator. This decorator must decorate a
        ``Class(AppState)`` that contains two methods: :py:meth:`register(self) <FeatureCloud.app.engine.app.AppState.register>` 
        and :py:meth:`run(self) <FeatureCloud.app.engine.app.AppState.run>`.

        * :py:meth:`register(self) <FeatureCloud.app.engine.app.AppState.register>`  must contain at least one call to 
          :py:meth:`self.register_transition('[anotherState]', [Role.COORDINATOR, Role.CLIENT, Role.BOTH]) <FeatureCloud.app.engine.app.AppState.register_transition>`

        * :py:meth:`run(self) <FeatureCloud.app.engine.app.AppState.run>` implements all logic in the state. 
          Use ``return '[anotherState]'`` to change to the next state.
          To ensure that only the coordinator/only a client does something, use :meth:`self.is_coordinator <FeatureCloud.app.engine.app.AppState.is_coordinator>`

        * To keep variables between *states*, you can use :py:meth:`self.store(key='[someKey]', value=[variablename]) <FeatureCloud.app.engine.app.AppState.store>` to store a variable 
          and :meth:`self.load('[someKey]') <FeatureCloud.app.engine.app.AppState.load>` to load the variable in another state.

      * For communication, use the methods :meth:`self.gather_data <FeatureCloud.app.engine.app.AppState.gather_data>`, 
        :meth:`self.await_data <FeatureCloud.app.engine.app.AppState.await_data>`,
        :meth:`send_data_to_participant <FeatureCloud.app.engine.app.AppState.send_data_to_participant>`, 
        :meth:`send_data_to_coordinator <FeatureCloud.app.engine.app.AppState.send_data_to_coordinator>`, 
        :meth:`self.send_data_to_coordinator <FeatureCloud.app.engine.app.AppState.send_data_to_coordinator>`,
        :meth:`self.aggregate_data <FeatureCloud.app.engine.app.AppState.aggregate_data>`

    * *Using external packages:* if you want to use an external package, e.g. ``numpy``, you must 
      ``import numpy`` in `states.py` and include ``numpy`` with the wanted version 
      in `requirements.txt`

    * *Logging:* for logging, use :meth:`self.log <FeatureCloud.app.engine.app.AppState.log>` 
      and :meth:`self.update <FeatureCloud.app.engine.app.AppState.update>`
    
    For more information, checkout the :meth:`code documentation <FeatureCloud.app.engine.app.AppState>`
    and an app template, e.g checkout :ref:`template app dice <app dice>`.
    Alternatively, you can also check the :ref:`example provided here <example states>`

2. Build your application (creates a docker image of the application)

``featurecloud app build ./my-app my-app``

.. _testing anchor:

4. Test your application with Testbed

  * Start the controller with
    ``featurecloud controller start``
    This creates a folder called `data` in your current working directory

  * Place your input data into the `data` folder just created. For EACH client 
    you want to simulate in a test, create a folder, e.g. `client1`, `client2`, ...
    Also, create a folder `generic_dir` for the data that all clients should get

  * Start a test with
    ``featurecloud test start --controller-host=http://localhost:8000 --app-image=my-app --query-interval=1 --client-dirs=.,.``

  * You can checkout the results on the frontend (featurecloud.ai).
    You need to be logged in, then test results are found `here <https://featurecloud.ai/development/test>`_. 

5. Publish your application to the FeatureCloud App Store 
    * First, you must create the app in the app store. You must be logged in as
      a user with the role app developer. Then, in the *App Store* under *Development*,
      you can add an application. 
    
    * Secondly, you must push the built image with the cli
      ``featurecloud app publish my-app``
      Ensure that the name you used with ``featurecloud app build`` is the same
      as the one you gave before creating the app in the *App store* Frontend.

.. _app templates:

**Available app templates:**

* **Blank app:** The `Blank app template <https://github.com/FeatureCloud/app-blank/>`_ is a starting point for implementing apps by adding more states and operations.

* **Blank app with visualizer:** `This template <https://github.com/FeatureCloud/app-blank-with-visualizer/>`_ is based on the blank app template and it includes a visualizer application.

* **App round:** The `App round template <https://github.com/FeatureCloud/app-round/>`_ is based in the blank app template with three app states implemented.

.. _app dice:

* **Dice app:** The `Dice app template <https://github.com/FeatureCloud/app-dice/>`_ contains four states with a simple dice throw simulation.

* **App Four:** The `App Four template <https://github.com/FeatureCloud/app-four/>`_ contains four states and supports three scenarios (Centralized, Simulation, and Federated) in two modes (Native and Containerized).

.. _example states:

**Example of states.py**
::

  # A simple example for a typical federated learning app
  from FeatureCloud.app.engine.app import AppState, app_state, Role, LogLevel

  # an intial state for loading the data, this state MUST always be implemented
  @app_state("initial")
  class InitialState(AppState): # you can choose any fitting classname
    def register(self):
      # here, any possible change to another state must be documented
      self.register_transition("local_computation", Role.BOTH)
        # Role.BOTH means that this transition can be done by
        # the coordinator and a participant
        # Other options are Role.PARTICIPANT and Role.COORDINATOR
    def run(self):
      # Here you can for example load the config file and the data
      # Any data given by the user will always be placed in the directory
      # given in the line below (<workind_dir>/mnt/input)
      dataFile = os.path.join(os.getcwd(), "mnt", "input", "data.csv"))
      data = pd.read_csv(dataFile)
      # Data can be stored for access in other states like this
      self.store(key = "data", value=data)
      # Also store some intial model
      self.store(key = "model", value=np.zeros(5))
      # to progress to another state, simply return the states name
      return "local_computation"

  # a state for the local computation
  @app_state
  class local_computation(AppState):
    def register(self):
      self.register_transition("aggregate_data", Role.COORDINATOR)
      self.register_transition("obtain_weights", Role.PARTICIPANT)

    def run(self):
      # do some local computations
      model = calculateThings(self.load("data"), self.load("model"))
        # loads the data and calculates some model
      self.send_data_to_coordinator(model,
                                  send_to_self=True,
                                  use_smpc=False)
      if self.is_coordinator:
        return "aggregate"
      else:
        return "obtain_weights"

  # a state just for obtaining the weights from the coordinator
  @app_state("obtain_weights")
  class obtainWeights(AppState):
    def register(self):
      self.register_transition("local_computation", Role.BOTH)

    def run(self):
      updated_model = self.await_data(n = 1)
        # n=1 since we only expect one model from the coordinator
      self.store("model", updated_model)
      return "local_computation"

  # a state for the coordinator to aggregate all weights
  @app_state("aggregate_data")
  class aggregateDataState(AppState):
    def register(self):
      self.register_transition("obtain_weights", Role.COORDINATOR)
      self.register_transition("terminal", Role.COORDINATOR)
    def run(self):
      aggregated_model = self.aggregate_data(operation = SMPCOperation.ADD)
        # waits for every participant to send something and then
        # adds them together
      updated_model = aggregated_model / len(self.clients)
      if stop_training_criteria: # if the training is done
        fp = open(os.path.join("mnt", "output", "trained_model.pyc"), "wb")
        np.save(fp, updated_model)
        return "terminal"
          # going to the terminal state will finnish the app and tell
          # all clients that the computation is done
      else:
        self.broadcast_data(updated_model, send_to_self = True)
        return "obtain_weights"

.. _getting started dev from scratch anchor:

Developing applications from scratch (advanced)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Steps for creating your federated application from scratch:

1. Using any language of your choice, create a HTTP-Server that accepts requests
   from the *controller*. To do that, the HTTP-Server should listen to localhost
   on port 5000. It must support the API as 
   :doc:`documented in the API documentation <API>`. The api must be implemented
   on the route `/api`. Furthermore, the route `/web` has to be supported for
   `GET/web` requests. The response to `GET/web` is a simple text string 
   with the current status.

2. Build Docker image from your application: ``docker build --no-cache -t my-app ./my-app``

3. Test your application: FeatureCloud provides a `Testbed <https://featurecloud.ai/development/test/>`_.
   The usage is the same as when developing with the python templates, :ref:`see here <testing anchor>`

4. Tag and push your application in FeatureCloud App Store:

- Tag your app: ``docker tag <Image_ID> featurecloud.ai/my-app``

- Login to our Docker registry with your FeatureCloud.ai user credentials: ``docker login featurecloud.ai``

- Push your app: ``docker push featurecloud.ai/my-app``


Additional features of FeatureCloud
-----------------------------------
1. Privacy enhancing techniques:

   * :ref:`Secure MultiParty Computation (SMPC) <smpc anchor>`

   * :ref:`Differential Privacy (DP) <dp anchor>`

Links to blog articles
----------------------

Create an app
^^^^^^^^^^^^^
In `this story <https://medium.com/developing-federated-applications-in-featurecloud/create-your-first-featurecloud-app-daced512eb45/>`_ we detail the steps for creating your application in FeatureCloud.

Run app in Testbed
^^^^^^^^^^^^^^^^^^
`Read <https://medium.com/developing-federated-applications-in-featurecloud/run-an-app-in-fc-test-bed-b4b0ecae08b0/>`_  about FeatureCloud Testbed and how can it accelerate the your application testing.

Communicate data
^^^^^^^^^^^^^^^^
`How to handle communication <https://medium.com/developing-federated-applications-in-featurecloud/communicate-data-across-clients-77b4d9fc8258/>`_ between participants in your federated application.

Publish your app
^^^^^^^^^^^^^^^^
`Steps <https://medium.com/developing-federated-applications-in-featurecloud/featurecloud-ai-store-publish-your-applications-2afb90c26a8d/>`_ for publishing your application in FeatureCloud App Store.

Run app with GPU
^^^^^^^^^^^^^^^^
`Read all <https://medium.com/developing-federated-applications-in-featurecloud/run-featurecloud-applications-with-gpu-acceleration-39cfec98f952/>`_ about using GPU support in your application.

.. _dev from scratch anchor:
