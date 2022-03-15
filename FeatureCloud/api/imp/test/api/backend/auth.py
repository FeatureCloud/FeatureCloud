import json
from pathlib import Path

from FeatureCloud.api.utils.cli.helper import http

home = str(Path.home())
url = 'http://127.0.0.1:7000'


def is_user_logged_in():
    headers = create_authorization_header()
    r = http.get(url=f'{url}/user/info/', headers=headers)
    if r.status_code == 200:
        return True
    else:
        print("No user is logged in. Please login first.")
        exit()
        return False


def login(email: str, password: str):
    r = http.post(url=f'{url}/auth/login/',
                  json={'username': email,
                        'password': password})
    if r.status_code == 200:
        refresh, access = r.json()['refresh'], r.json()['access']
        login_details = {'email': email, 'password': password, 'refresh': refresh, 'access': access}
        login_details = json.dumps(login_details)
        file = open(f'{home}/.fc_cli', 'w')
        file.write(login_details)
        file.close()
        return True
    else:
        return False


def logout():
    r = http.post(url=f'{url}/auth/logout/',
                  json={'refresh': None})
    if r.status_code == 200:
        with open(f'{home}/.fc_cli', 'w') as file:
            file.write('')
        file.close()
        return True
    else:
        print(r.content)
        return False


def create_authorization_header():
    with open(f'{home}/.fc_cli') as jsonFile:
        access_token = json.load(jsonFile)['access']
        jsonFile.close()
    return {"Authorization": f'Bearer {access_token}'}
