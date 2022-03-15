from pathlib import Path

from FeatureCloud.api.utils.cli.api.backend.auth import create_authorization_header
from FeatureCloud.api.utils.cli.helper import http

home = str(Path.home())
url = 'http://127.0.0.1:7000'


def info(project_id: str or int):
    headers = create_authorization_header()
    r = http.get(url=f'{url}/projects/{project_id}', headers=headers)
    if r.status_code == 200:
        return r.json()
    else:
        return False


def create(name: str, description: str):
    headers = create_authorization_header()
    r = http.post(url=f'{url}/projects/',
                  json={'name': name,
                        'description': description},
                  headers=headers
                  )

    if r.status_code == 200:
        return r.json()['id']
    else:
        return False


def remove(proj_id: str or int):
    headers = create_authorization_header()
    r = http.delete(url=f'{url}/projects/{proj_id}/', headers=headers)

    if r.status_code == 200:
        return True
    else:
        return False


def list_projects():
    headers = create_authorization_header()
    r = http.get(url=f'{url}/projects/', headers=headers)

    if r.status_code == 200:
        return r.json()
    else:
        return False


def list_tokens(project_id):
    headers = create_authorization_header()
    r = http.get(url=f'{url}/project-tokens/{project_id}/', headers=headers)
    if r.status_code == 200:
        return r.json()
    else:
        return False


def create_token(project_id: str or int):
    headers = create_authorization_header()
    r = http.post(url=f'{url}/project-tokens/{project_id}/',
                  json={'cmd': 'create'},
                  headers=headers
                  )

    if r.status_code == 200:
        return r.json()
    else:
        return False


def remove_token(token_id: str or int):
    headers = create_authorization_header()
    r = http.delete(url=f'{url}/project-tokens/token/{token_id}/', headers=headers)

    if r.status_code == 200:
        return r.json()
    else:
        print(r.status_code)
        print(r.text)
        return False
