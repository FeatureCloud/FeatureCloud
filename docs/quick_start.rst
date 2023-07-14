==========
Quickstart
==========
This pip package is intended to be used with the `FeatureCloud <https://featurecloud.ai/>`_ privacy-preserving platform for federated learning and data-analysis.

Prerequisites
-------------
Install Python

Installation
------------
``pip install featurecloud``

Main commands
-------------

========================= ==================================================
Command                   Description
========================= ==================================================
**app**                   App related commands
**controller**            Controller start/stop
**test**                  Testbed related commands
========================= ==================================================

More details about commands and its subcommands are available in the command line ``--help`` option

App template based development
------------------------------

1. Check out our app templates below

2. Create and implement an application based on a template

``featurecloud app new --template-name=app-blank app-blank``

3. Build your application

``featurecloud app build ./app-blank my-app``

4. Test your application with Testbed

``featurecloud test start --controller-host=http://localhost:8000 --app-image=my-app --query-interval=1 --client-dirs=.,.``


Available app templates
-----------------------

Blank app
^^^^^^^^^
The `Blank app template <https://github.com/FeatureCloud/app-blank/>`_ is a starting point for implementing apps by adding more states and operations.

Blank app with visualizer
^^^^^^^^^^^^^^^^^^^^^^^^^
`This template <https://github.com/FeatureCloud/app-blank-with-visualizer/>`_ is based on the blank app template and it includes a visualizer application.

App round
^^^^^^^^^
The `App round template <https://github.com/FeatureCloud/app-round/>`_ is based in the blank app template with three app states implemented.

Dice app
^^^^^^^^
The `Dice app template <https://github.com/FeatureCloud/app-dice/>`_ contains four states with a simple dice throw simulation.

App Four
^^^^^^^^
The `App Four template <https://github.com/FeatureCloud/app-four/>`_ contains four states and supports three scenarios (Centralized, Simulation, and Federated) in two modes (Native and Containerized).


How to?
-------
Check out our Medium post collection regarding frequently asked questions during app development!

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
