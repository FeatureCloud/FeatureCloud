===============
Getting Started
===============

The FeatureCloud pip package
----------------------------

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

1. Create a directory with the wanted template (:ref:`templates <app templates>`), we suggest starting with :ref:`App Four <app four>`

``featurecloud app new --template-name=app-four my-app``

2. Implement your own application using the template TODO: add a link for more info
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
    and the recommended :ref:`template app four <app four>`

3. Build your application (creates a docker image of the application)

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

* **Dice app:** The `Dice app template <https://github.com/FeatureCloud/app-dice/>`_ contains four states with a simple dice throw simulation.

.. _app four:

* **App Four:** The `App Four template <https://github.com/FeatureCloud/app-four/>`_ contains four states and supports three scenarios (Centralized, Simulation, and Federated) in two modes (Native and Containerized).

Developing applications from scratch (advanced)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Steps for creating your federated application from scratch:

1. Using any language of your choice, create a HTTP-Server that accepts requests
   from the *controller*. 
   
.. TODO: create API Spezifications and link them, create them from OPENAPI document
   TODO: talk about the ports as well, controller querries port 9000 and 9001 somehow, 
   also Docker conditions the app must uphold so the controller finds it?

2. Build Docker image from your application: ``docker build --no-cache -t my-app ./my-app``

3. Test your application: FeatureCloud provides a `Testbed <https://featurecloud.ai/development/test/>`_.
   The usage is the same as when developing with the python templates, :ref:`see here <testing anchor>`

4. Tag and push your application in FeatureCloud App Store:

- Tag your app: ``docker tag <Image_ID> featurecloud.ai/my-app``

- Login to our Docker registry with your FeatureCloud.ai user credentials: ``docker login featurecloud.ai``

- Push your app: ``docker push featurecloud.ai/my-app``


Additional features of FeatureCloud
-----------------------------------
.. TODO! Just this list, keep it short and just reference to the real stuff
   GPU
   Using privacy-preserving techniques (SMPC and DP)
   Offering a frontend to users
   More Features?

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
