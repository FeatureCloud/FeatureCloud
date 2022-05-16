import git
import os
from urllib.parse import urljoin
import docker
import tqdm

from FeatureCloud.api.imp.util import getcwd_fslash


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
    (None, msg): msg: str

    """
    repo = git.Repo.clone_from(create_link(template_name), os.path.join(directory, name), )
    repo.delete_remote('origin')
    msg = 'Ready to develop! Enjoy!'
    return (None, msg)


def build(path: str = ".", image_name: str = None, tag: str = "latest", rm: str = True):
    """ Build app image,
     Once on image_name is provided the name of the current directory will be used.
     Also, the current directory will be searched for the Dockerfile.

    Parameters
    ----------
    path: str
        path to the directory containing the Dockerfile
    image_name: str
        name of the app's docker image
    tag: str
        tag for the image name
    rm: bool
        if True, remove intermediate containers
    Returns
    -------

    """
    if image_name is None:
        image_name = getcwd_fslash().split("/")[-1]
    client = docker.from_env()
    build_proc = client.api.build(path=path, tag=f"{image_name}:{tag}", rm=rm)
    log(build_proc, description=f"Building {image_name}:{tag} ...")
    return None, None


def download(name: str, tag: str = "latest"):
    """ Download a given docker image from FeatureCloud.ai docker repo.

    Parameters
    ----------
    name: image name
    tag: tag

    """
    name, msg = fc_repo_name_check(name, tag)
    if name is not None:
        client = docker.from_env()
        pull_proc = client.api.pull(repository=name, tag=tag)
        log(pull_proc, description=f"Downloading {name} ...")
    return None, msg


def fc_repo_name_check(name, tag):
    msg = ""
    if "featurecloud.ai/" not in name:
        if "/" in name:
            correct_name = f"featurecloud.ai/{name.strip().split('/')[-1]}:{tag}"
            msg = f"The app docker image name {name}:{tag} is not correct.\n{correct_name} can be an acceptable name!"
            return None, msg
        name = f"featurecloud.ai/{name}"
        msg = f"The complete name should include the FeatureCloud docker repository address." \
              f"\nThe app name is completed: {name}\n"
        return None, msg
    return name, msg


def log(proc, description):
    for _ in tqdm.tqdm(proc, desc=description):
        pass


def publish(name: str, tag: str = "latest"):
    """ Push a given app into FeatureCloud.ai docker repo.

    Parameters
    ----------
    name: image name
    tag: tag

    """
    name, msg = fc_repo_name_check(name, tag)
    if name is not None:
        client = docker.from_env()
        push_proc = client.api.push(repository=name, tag=tag)
        log(push_proc, description=f"Uploading {name}:{tag} ...")
    return None, msg


def remove(name: str):
    """ Delete docker image from local hard drive.

    Parameters
    ----------
    name: image name

    """
    client = docker.from_env()
    client.images.remove(image=name)
    return None, None
