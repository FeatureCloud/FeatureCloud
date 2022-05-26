import git
import os
from urllib.parse import urljoin
import docker

from git import GitError

from FeatureCloud.api.imp.exceptions import FCException
from FeatureCloud.api.imp.util import getcwd_fslash, get_docker_client


def create_link(template_name: str) -> str:
    TEMPLATE_URL = 'https://github.com/FeatureCloud/'
    return urljoin(TEMPLATE_URL, template_name + '.git')


def new(name: str, directory: str = '.', template_name: str = 'app-blank') -> str:
    """
    Parameters
    ----------
    name: str
        app name
    directory: str
        path to create the app's directory in
    template_name: str
        a template repository in FeatureCloud repositories
    Returns
    -------
    str
        path to the created app
    Raises
    -------
         FeatureCloud.api.imp.exceptions.FCException
    """
    try:
        app_path = os.path.join(directory, name)
        repo = git.Repo.clone_from(create_link(template_name), app_path)
        repo.delete_remote('origin')
        return app_path
    except GitError as e:
        raise FCException(e)


def build(path: str = ".", image_name: str = None, tag: str = "latest", rm: str = True):
    """ Build app image.

    Parameters
    ----------
    path: str
        path to the directory containing the Dockerfile
    image_name: str
        name of the app's docker image. If not provided, the name of the current directory will be used.
    tag: str
        versioning tag
    rm: bool
        if True, remove intermediate containers
    Returns
    -------
    lines
       generator providing information about the build progress
    Raises
    -------
         FeatureCloud.api.imp.exceptions.FCException
    """
    if image_name is None:
        image_name = getcwd_fslash().split("/")[-1]

    client = get_docker_client()
    try:
        if not os.path.exists(os.path.join(path, 'Dockerfile')):
            raise FCException(f'Dockerfile not found in directory: {os.path.abspath(path)}')

        for line in client.api.build(path=path, tag=f"{image_name}:{tag}", rm=rm):
            # "message" indicates an error, e.g.:
            # b'{"message":"Cannot locate specified Dockerfile: Dockerfile"}\n'
            _, _, err_msg = line.partition(b'"message":')
            if err_msg != b'':
                raise FCException(err_msg.decode().lstrip('"').rstrip().rstrip('"}'))

            yield line
    except docker.errors.DockerException as e:
        raise FCException(e)


def download(name: str, tag: str = "latest"):
    """ Download a given docker image from FeatureCloud.ai docker repo.

    Parameters
    ----------
    name: str
        image name
    tag: str
        versioning tag
    Returns
    -------
    lines
       generator providing information about the download progress
    Raises
    -------
         FeatureCloud.api.imp.exceptions.FCException
    """
    fc_name = fc_repo_name(name)
    client = get_docker_client()
    try:
        for line in client.api.pull(repository=fc_name, tag=tag):
            yield line
    except docker.errors.DockerException as e:
        raise FCException(e)


def publish(name: str, tag: str = "latest"):
    """ Push a given app into FeatureCloud.ai docker repo.

    Parameters
    ----------
    name: str
        image name
    tag: str
        versioning tag
    Returns
    -------
    lines
       generator providing information about the publish progress
    Raises
    -------
         FeatureCloud.api.imp.exceptions.FCException
    """
    fc_name = fc_repo_name(name)
    client = get_docker_client()

    try:
        client.images.get(name).tag(fc_name)
    except docker.errors.DockerException as e:
        raise FCException(e)

    try:
        for line in client.api.push(repository=fc_name, tag=tag):
            yield line
    except docker.errors.DockerException as e:
        raise FCException(e)


def remove(name: str):
    """ Delete docker image from local hard drive.

    Parameters
    ----------
    name: str
        image name
    Raises
    -------
         FeatureCloud.api.imp.exceptions.FCException
    """
    client = get_docker_client()
    try:
        client.images.remove(image=name)
    except docker.errors.DockerException as e:
        raise FCException(e)


def fc_repo_name(name):
    if not name.startswith("featurecloud.ai/"):
        return f'featurecloud.ai/{name}'

    return name
