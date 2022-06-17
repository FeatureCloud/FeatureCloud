import git
import os
from urllib.parse import urljoin
import docker
from docker import DockerClient

from git import GitError

from FeatureCloud.api.imp.exceptions import FCException
from FeatureCloud.api.imp.util import getcwd_fslash, get_docker_client

FC_REPO_PREFIX = "featurecloud.ai/"


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

    if not template_name.startswith('app-'):
        raise FCException(f'{template_name} is not a valid template. Please see the help for available templates')

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
        # Docker would also check for Dockerfile, but if, by accident, a path is provided with many sub folders
        # it just takes too long. So we check it upfront:
        if not os.path.exists(os.path.join(path, 'Dockerfile')):
            raise FCException(f'Dockerfile not found in directory: {os.path.abspath(path)}')

        for entry in client.api.build(path=path, tag=f"{image_name}:{tag}", rm=rm, decode=True):
            # Examples of stream entries, 'message' indicates error:
            # {'stream': 'Step 2/11 : RUN apt-get update && apt-get install -y supervisor nginx'}
            # {'message': 'Cannot locate specified Dockerfile: Dockerfile'}
            if 'message' in entry:
                raise FCException(entry['message'])

            yield entry
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
        for entry in client.api.pull(repository=fc_name, tag=tag, stream=True, decode=True):
            if 'error' in entry:
                raise FCException(entry['error'])

            yield entry
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
        local_repo = f'{name}:{tag}'
        registry_repo = f'{fc_name}:{tag}'
        client.images.get(local_repo).tag(registry_repo)
    except docker.errors.DockerException as e:
        raise FCException(e)

    try:
        for entry in client.api.push(repository=registry_repo, stream=True, decode=True):
            # Examples of stream entries:
            # {'status': 'Waiting', 'progressDetail': {}, 'id': '38feb0548c7a'}
            # {'errorDetail': {'message': 'unauthorized: authentication required'}, 'error': 'unauthorized: authentication required'}
            if 'error' in entry:
                raise FCException(entry['error'])

            yield entry
    except docker.errors.DockerException as e:
        raise FCException(e)


def remove(name: str, tag: str = "latest"):
    """ Delete docker image from local hard drive.

    Parameters
    ----------
    name: str
        image name
    tag: str
        the versioning tag to be removed. If set to 'all', all versions will be deleted.
    Raises
    -------
         FeatureCloud.api.imp.exceptions.FCException
    """
    to_find = name if tag == 'all' else f'{name}:{tag}'
    client = get_docker_client()
    removed = remove_images(client, to_find)

    if tag == 'all':
        # search also for local images containing the FC repository name
        to_find = fc_repo_name(name)
        removed = removed + remove_images(client, to_find)

    return removed


def fc_repo_name(name: str) -> str:
    if not name.startswith(FC_REPO_PREFIX):
        return f'{FC_REPO_PREFIX}{name}'

    return name


def remove_images(client: DockerClient, to_find: str):
    removed = []
    for img in client.images.list(to_find):
        # one image id may have several tags
        for img_tag in img.tags:
            try:
                client.images.remove(image=img_tag, force=True)
            except docker.errors.DockerException as e:
                raise FCException(e)
        removed = removed + img.tags

    return removed
