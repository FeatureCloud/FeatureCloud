.. _workflow anchor:

FeatureCloud Workflow
=====================

In FeatureCloud, end-users and developers can run linear workflow in the
front-end website at
`https://featurecloud.ai <https://featurecloud.ai/>`__. They can
assemble a workflow and run different apps in a linear fashion where
each app will be executed after another. Results of each app will be
provided for the next one in the workflow while the results should be in
the right format and extension which is acceptable for the upcoming app.
Any workflows may involve different number of clients(data owners) who
want to collaborate in the federated fashion, using one or more
applications. Even though the online workflow serves all the needs of
end-users, developers may have challenges to flexibly employ different
apps in nonlinear fashion to come-up with new solutions. FeatureCloud
developers can range from app developers who will implement federated
apps that are extended version of centralized, or the ones that are
introduced originally to address federated challenges. The Latter is
concerned with researchers in various fields of science which makes it
significantly trickier. In fact, developers may need arbitrary
operations on data and results for to discover the right solution which
may involve pre-/post-processing apps or operations. Long story short,
here we introduce FeatureCloud test workflow, where developers can
assemble an arbitrary workflow for research purposes. Such test
workflows, are not supported in the app store, and once the developers
came with final solution, they ought to present it as an app that may be
run in conjunction of other apps in a workflow. In FC test workflow,
each app will be run as a test app in the test-bed. Accordingly, all the
functionalities are applied to the test-run that runs a specific app.

FeatureCloud Controller Class
=============================

FeatureCloud pip package includes the Controller class that used to be
extended by developers for defining test apps and workflows. The
Controller class cover basic interactions with the FC controller. The
functionalities are:

-  start: start a given test-run
-  stop: stops a given test-run
-  delete: deletes a given test-run
-  list: list all the test-runs in the controller
-  traffic: gets the test-run’s traffic from the controller
-  logs: Gets all the logs for a given test-run from the controller
-  info: Gets information for a given test-run from the controller

All the operations are regarding the predetermined controller where it
is possible to run multiple controller instances on the same machine.
Such functionalities and interactions can be useful for any app and in
some cases for the workflow as a whole. Therefore, we introduce TestApp
and TestWorkFlow class to cover such basic functionalities.

TestApp
=======

In a workflow, during the execution of each app, developers may need a
limited set of interactions with controller to manipulate data or
results. Beside such operations, most apps need to get data and provide
results. In that regard, we provided some attributes and methods to
handle automatic data loading, intermediate result extractions and
storage. ## Attributes:

App’s docker image name
-----------------------

``app_image``: The image name of the app in FeatureCloud docker
repository. ### ID of the test run for the app ``test_id``: ID of the
test-run for the app. This ID should be used to inform the controller.

Number of clients
-----------------

``n_clients``: Number of clients that app will run for

Data extraction flag
--------------------

``results_ready``: It is true once the results are extracted to the
app’s directory

ID of the application in a test workflow
----------------------------------------

``app_id``: ID of app in the workflow that contains multiple apps can be
helpful to recognise it once the app is run in a non-linear workflow.

Paths to data
-------------

To have access to the data of apps before and after execution,
developers may need to use these attributes. Meanwhile, the controller
needs relative paths to data and tests directories of the controller to
clone the initial data and files or store the final results.

Path to the generic data for app’s clients
------------------------------------------

``generic_dir``: Relative path to directory containing generic files,
e.g., config.yml file. To be used by developers to access th edata.

Path to the private data for app’s clients
------------------------------------------

``clients_path``: Full path to directory containing the clients’ data
that can be used by developers to access the data.

Relative path to the private data for app’s clients
---------------------------------------------------

``clients_relative_path``: Relative path to directory containing the
clients’ data which should be provided to the controller to store the
results to.

Path to the results of the app execution
----------------------------------------

``results_path``: Full path to directory containing the app’s results
for clients. Not all apps provide specific results for clients. In that
case, there may be different number of ``zip`` files as results than
number of clients. Full path will be needed when developers may want to
access the data.

.. _relative-path-to-the-private-data-for-apps-clients-1:

Relative path to the private data for app’s clients
---------------------------------------------------

``results_relative_path``: Relative path to directory containing the
app’s results for clients.

Methods
-------

Set apps test ID
~~~~~~~~~~~~~~~~

``def set_id(self, test_id: int)``: Set the app’s test ID and partially
define the delete method based on it.

Extract the results (zip files)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``def extract_results(self, def_res_file: str)``: extract app’s results
zip files for all clients into their corresponding directories

Wait for the end of app execution
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``def wait_until_finishes(self)``: Waits until the app status becomes
finished.

Check the app is finished or not
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``def is_finished(self)``: Check either the app status is finished.

Create and remove directories
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``def clean_dirs(self, def_re_dir: str)``: creates results directories.
And removes existing results in the directories

Generate paths to data and results dirs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``def create_paths(self, ctrl_data_path: str, ctrl_test_path: str)``:
Generate paths to directories containing the app’s data(for each client)
And also for app’s results.

::

   Parameters
   ----------
   ctrl_data_path: str
       path to the target controller's data folder
   ctrl_test_path: str
       path to the target controller's tests folder

Copy final results, as data for the next app.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``def copy_results(self, ctrl_data_path: str, dest_generic: str, dest_clients: list, default_res_name: str)``:
Copy results of the app to as the data to the directory of the next app.

::

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

TestWorkFlow
------------

The TestWorkFlow class is an abstract class that provides basic
functionalities for general workflows. It asks developers to extend it
and implement run() and register_app methods. ### Attributes #### apps
It includes a list of instances of TestApp class as apps that should be
run in the workflow. The order of registering apps will be preserved,
however, developers can run them in any arbitrary manner. ####
controller An instance of Controller class that helps developers to have
same operations for all running test-runs with different apps. ####
default_res_dir_name It is a name for the result directory that contains
all extracted results from the zip file for each client in each app.
This directory provides the data for the upcoming app. ### Methods

Registering an app: ``def register_app(self)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This abstract method should be implemented by developers to register
apps into the workflow. The apps will be added to the ``self.apps`` list
and will be available in the run method to be executed.

Running the workflow: ``def run(self)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It is another abstract method tha should be implemented by developers to
run the workflow. Developers can implement an arbitrary flow of app
execution when they have access to the data and results of each app.

Registering a TestApp instance ``def register(self, app)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Adding ``TestApp`` instance to the app list and logging the apps
attributes.

Stopping all running apps on the WF’s controller: ``def stop(self)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Stop all test-runs in the controller. #### Deleting all the running
containers in the WF: ``def delete(self)`` Delete all test-runs in the
controller.

Getting information of all running test-runs in the WF’s controller: ``def info(self, format: str)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

info of all tests in the specified controller or all of them.

Tips for implementing and running workflows
-------------------------------------------

For implementing a desired workflow, developers should extend
``TestWorkFlow`` class and implement ``register_apps`` and ``run``
methods. The name of the extended class should always be ``WorkFlow``
and it asks for the controller address, channel, and query interval for
querying the controller. After implementing the workflow, developers can
run it using FeatureCloud pip package:

::

   sudo featurecloud test workflow start --wf-dir <WORKFLOW_FILE_Path> --wf-file <NAME> --controller-host <CONTROLLER> --channel <> --query-interval <>

Beware that due to the file permissions, the workflow should be run
using supper-user access. ALl the data and results will be available in
the controller’s data directory. In fact, data for the first app should
be provided in ``app{app_n}`` folder. Where ``app_n`` is the index the
target app in WF’s ``apps`` list. The same numbering applies for all the
registered apps, and results will be directly moved into the next app’s
directory. Even though the controller write result zip files in
``tests`` directory, for each app, the extracted results will be
available in corresponding app folder in ``data`` directory.
