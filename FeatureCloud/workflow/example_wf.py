from FeatureCloud.workflow.workflow import TestWorkFlow
from FeatureCloud.workflow.app import TestApp
from time import sleep
from functools import partial


class WorkFlow(TestWorkFlow):
    """ Example workflow containing following apps:
        1- featurecloud.ai/fc_cross_validation
        2- featurecloud.ai/basic_rf
        3- featurecloud.ai/fc_roc

        Methods:
        --------
        register_apps(): registering the apps
        run(): running apps with the same order as registration

    """
    def __init__(self, controller_host: str, channel: str, query_interval: str):
        super().__init__(controller_host, channel, query_interval)

        self.controller_path = "/home/mohammad/PycharmProjects/FeatureCloud/data"
        self.ctrl_data_path = f"{self.controller_path}"
        self.ctrl_test_path = f"{self.controller_path}/tests"

        self.generic_dir = {}
        self.n_clients = 2
        self.TestApp = partial(TestApp,
                               n_clients=self.n_clients,
                               ctrl_data_path=self.ctrl_data_path,
                               ctrl_test_path=self.ctrl_test_path,
                               controller_host=controller_host,
                               channel=channel,
                               query_interval=query_interval)

    def register_apps(self):
        """ Registering the three apps.

        """
        app_id = 0
        app1 = self.TestApp(app_id=app_id, app_image="featurecloud.ai/fc_cross_validation")
        self.register(app1)

        app_id += 1
        app2 = self.TestApp(app_id=app_id, app_image="featurecloud.ai/basic_rf")
        self.register(app2)

        app_id += 1
        app3 = self.TestApp(app_id=app_id, app_image="featurecloud.ai/fc_roc")
        self.register(app3)

    def run(self):
        """ Running apps with the same registration order,
            logging the app execution,
            setting the ID
            waiting until the app execution is finished
            extracting the result to the app's directory
            Waiting until the extraction is over
            Delete the test run for the app
            Copy the results as data for the next app

        """
        print("Workflow execution starts ...")
        for i, app in enumerate(self.apps):
            app.clean_dirs(self.default_res_dir_name)
            id = app.start()
            app.set_id(id)
            print(f"{app.app_image}(ID: {app.test_id}) is running ...")
            app.wait_until_finishes()
            print("App execution is finished!")
            app.extract_results(self.default_res_dir_name)
            print("extracting the data...")
            while not app.results_ready:
                sleep(5)
            print("Delete the app container...")
            app.delete()
            if i < len(self.apps) - 1:
                print(f"Move {app.app_image} results to the directory of the next app({self.apps[i + 1].app_image})")
                app.copy_results(ctrl_data_path=self.ctrl_data_path,
                                 dest_clients=self.apps[i + 1].clients_path,
                                 dest_generic=self.apps[i + 1].generic_dir,
                                 default_res_name=self.default_res_dir_name)
        print("Workflow execution is finished!")
