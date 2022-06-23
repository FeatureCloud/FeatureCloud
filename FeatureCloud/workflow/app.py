import os.path
from os import listdir
from pathlib import Path
import zipfile
from time import sleep
from FeatureCloud.workflow.controller import Controller
from functools import partial
import shutil
from distutils.dir_util import copy_tree


class TestApp(Controller):
    """
    Attributes:
    -----------
        app_image: str
            image name of the app in FeatureCloud docker repository
        test_id: int
            ID of the test running on a specific controller.
        n_clients: int
            Number of clients that app will run for
        results_ready: bool
            It is true once the results are extracted to the app's directory
        app_id: int
            ID of app in the workflow
        generic_dir: str
            Relative path to directory containing generic files
        clients_path: list
            Full path to directory containing the clients' data
        clients_relative_path: list
            Relative path to directory containing the clients' data
        results_path: str
            Full path to directory containing the app's results for clients
        results_relative_path: str
            Relative path to directory containing the app's results for clients
    Methods:
    --------
        set_id(test_id):
        extract_results(def_res_file):
        wait_until_finishes():
        clean_dirs(def_re_dir):
        create_paths(ctrl_data_path, ctrl_test_path):
        copy_results(ctrl_data_path, dest_generic, dest_clients, default_res_name):

    """
    def __init__(self, app_id, ctrl_data_path, ctrl_test_path, n_clients, app_image, **kwargs):
        super().__init__(**kwargs)
        if app_image.strip().startswith("featurecloud.ai/"):
            self.app_image = app_image.strip()
        else:
            self.app_image = f"featurecloud.ai/{app_image.strip()}"
        self.test_id = None
        self.n_clients = n_clients
        self.results_ready = False
        self.app_id = app_id
        self.generic_dir = ""
        self.clients_path = []
        self.clients_relative_path = []
        self.results_path = ""
        self.results_relative_path = ""
        self.create_paths(ctrl_data_path, ctrl_test_path)
        self.start = partial(self.start,
                             client_dirs=self.clients_relative_path,
                             generic_dir=self.generic_dir,
                             app_image=app_image,
                             download_results=self.results_relative_path)
        self.stop = partial(self.stop, self.test_id)

    def set_id(self, test_id: int):
        """ Set the app's test ID and partially define the
            delete method based on it.


        Parameters
        ----------
        test_id: int
        """
        self.test_id = test_id
        self.delete = partial(self.delete, test_id=self.test_id, del_all=None)

    def extract_results(self, def_res_file: str):
        """ extract app's results zip files for all clients
            into their corresponding directories

        Parameters
        ----------
        def_res_file: str
            Default name for the app's result directory
            Same name for all clients.

        """
        zip_files = [f for f in listdir(self.results_path) if f.endswith(".zip")]
        Path(self.results_path).mkdir(exist_ok=True, parents=True)
        if len(zip_files) > 1:
            print(f"Extracting the results of {self.app_image} ...")
            for zip_file in zip_files:
                client_n = int(zip_file.strip().split("client_")[-1].strip().split("_")[0])
                res_dir = f"{self.clients_path[client_n]}/{def_res_file}"
                zip_file_path = f"{self.results_path}/{zip_file}"
                if not os.path.exists(res_dir):
                    os.makedirs(res_dir, exist_ok=True)
                    print(f"Create {res_dir} directory...")
                with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                    zip_ref.extractall(res_dir)
                    print(f"Extract client {client_n} to {res_dir} directory...")
            self.results_ready = True
        else:
            print(f"Looking into {self.results_path}\n"
                  f"There is no file yet!\n"
                  "We will check again later....")
            sleep(5)
            self.extract_results(def_res_file)

    def wait_until_finishes(self):
        """ Waits until the app status becomes finished.

        """
        while not self.is_finished():
            sleep(5)

    def is_finished(self):
        """ Check either the app status is finished.

        """
        df = self.info(test_id=self.test_id, format='dataframe')
        # if df is None:
        #     print(msg)
        return df.status.values == "finished"

    def clean_dirs(self, def_re_dir: str):
        """ creates results directories.
            And removes existing results in the directories

        Parameters
        ----------
        def_re_dir: str
            Default name for the app's result directory
            Same name for all clients.
        """
        for c_dir in self.clients_path:
            print(c_dir, def_re_dir)
            if os.path.exists(f"{c_dir}/{def_re_dir}"):
                print(f"Delete {c_dir}/{def_re_dir}")
                shutil.rmtree(f"{c_dir}/{def_re_dir}")
        if os.path.exists(self.results_path):
            for zip_file in os.listdir(self.results_path):
                if zip_file.endswith(".zip"):
                    print(f"Delete {self.results_path}/{zip_file}")
                    os.remove(f"{self.results_path}/{zip_file}")
        else:
            Path(self.results_path).mkdir(exist_ok=True, parents=True)

    def create_paths(self, ctrl_data_path: str, ctrl_test_path: str):
        """ Generate paths to directories containing the app's data(for each client)
            And also for app's results.

        Parameters
        ----------
        ctrl_data_path: str
            path to the target controller's data folder
        ctrl_test_path: str
            path to the target controller's tests folder

        """
        self.results_relative_path = f"./results/app{self.app_id}"
        clients_relpath = [f"./app{self.app_id}/client_{c}" for c in range(self.n_clients)]
        self.clients_relative_path = ",".join(clients_relpath)
        self.clients_path = [f"{ctrl_data_path}{clients_relpath[c][1:]}" for c in
                             range(self.n_clients)]
        self.results_path = f"{ctrl_test_path}{self.results_relative_path[1:]}"
        self.generic_dir = f"./app{self.app_id}/generic"

    def copy_results(self, ctrl_data_path: str, dest_generic: str, dest_clients: list, default_res_name: str):
        """ Copy results of the app to
            as the data to the directory of the next app.

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

        """
        for client_n, client_res in enumerate(self.clients_path):
            res_dir = f"{client_res}/{default_res_name}"
            print(f"Copy {res_dir} to {dest_clients[client_n]} ...")
            copy_tree(res_dir, dest_clients[client_n])
        copy_tree(f"{ctrl_data_path}{dest_generic[1:]}",
                  f"{ctrl_data_path}{dest_generic[1:]}")
