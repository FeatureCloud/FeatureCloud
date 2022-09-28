import abc
from FeatureCloud.workflow.controller import Controller


class TestWorkFlow(abc.ABC):
    """ The abstract TestWorkFlow class to cover basic functionalities
        for FeatureCloud workflow.
        Non-linear streams
    Attributes:
    -----------
        apps: list of instances of TestApp in the workflow
        controller: an instance of Controller class
        default_res_dir_name: str
            the dir-name of apps' results
    Methods:
    --------
        register_apps():
        run():
        register(app):
        stop(controller_ind):
        delete(controller_ind):
        list(controller_ind, format):
        info(format, controller_ind):
    """

    def __init__(self, controller_host: str, channel: str, query_interval: str):
        self.apps = []
        self.controller = Controller(controller_host, channel, query_interval)
        self.default_res_dir_name = "AppResSults"

    @abc.abstractmethod
    def register_apps(self):
        """ Abstract method tha should be implemented
         by developers to register apps into the workflow.

        """

    @abc.abstractmethod
    def run(self):
        """ Abstract method tha should be implemented
            by developers to run the workflow.
        """

    def register(self, app):
        """ Adding TestApp instance to the app list
            and logging the apps attributes.

        Parameters
        ----------
        app: TestApp
            app instance to be registered.

        """
        self.apps.append(app)
        clients_dirs = "\n\t\t".join(app.clients_path)
        msg = f"{app.app_image} app is registered:\n" \
              f"\tController: {app.controller_host}\n" \
              f"\tClient data:\n" \
              f"\t\t{clients_dirs}\n" \
              f"\tGeneric data: {app.generic_dir}\n" \
              f"\tResult dir: {app.results_path}"
        print(msg)

    def stop(self):
        """ Stop all tests in the controller.

        """
        for test_id in self.controller.list():
            self.controller.stop(test_id)

    def delete(self):
        """ Delete all tests in the controller.

        """
        for test_id in self.controller.list():
            self.controller.delete(test_id)

    def info(self, format: str):
        """ info of all tests in the specified controller or all of them.

        """

        info_list = []
        for test_id in self.controller.list():
            info_list.append(self.controller.info(test_id, format))
        return info_list
