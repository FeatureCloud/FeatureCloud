import os
import shutil
import stat

import docker

from FeatureCloud.api.imp.exceptions import DockerNotAvailable


def getcwd_fslash():
    """
    Returns the current working directory and makes sure it contains forward slashes as separator.
    Hint: os.getcwd() result contains backslashes on Windows.
    """
    return os.getcwd().replace("\\", "/")


def get_docker_client():
    """
    Gets the docker client

    Raises:
         :py:class:`FeatureCloud.api.imp.exceptions.DockerNotAvailable`
            If the docker API cannot be reached.
    """
    try:
        client = docker.from_env()
        client.version()
        return client
    except docker.errors.DockerException:
        raise DockerNotAvailable()


def remove_dir(path_to_delete: str):
    """
    Replicates the Linux command 'rm -rf'
    """

    def remove_readonly(func, path, e):
        # shutil.rmtree doesn't have the force flag,
        # so we clear the readonly bit and reattempt the removal in the error handler
        os.chmod(path, stat.S_IWRITE)
        os.remove(path)

    shutil.rmtree(path_to_delete, onerror=remove_readonly)
