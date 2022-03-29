import git
import os
from urllib.parse import urljoin


def create_link(template_name: str) -> str:
    TEMPLATE_URL = 'https://github.com/FeatureCloud/app-blank.git'
    return urljoin(TEMPLATE_URL, template_name+'.git')

def new(name: str, directory: str = '.', template_name: str = 'app-blank') -> str:
    repo = git.Repo.clone_from(create_link(template_name), os.path.join(directory, name))
    repo.delete_remote('origin')
    msg = 'Ready to develop! Enjoy!'
    return (None, msg)
