import requests
from urllib.parse import urlencode

from FeatureCloud.api.imp.test.helper import http


def is_online(url: str = 'http://localhost:8000/'):
    try:
        requests.get(url=url)
        return True
    except requests.exceptions.ConnectionError:
        return False


def start_test(url: str, docker_image: str, directories: [], generic_directory: str, is_local_relay: bool,
               query_interval: str or int, download_results: str):
    """
    Start a new test
    :param url:
    :param docker_image:
    :param directories:
    :param generic_directory
    :param is_local_relay:
    :param query_interval:
    :param download_results:
    :return:
    """

    response = http.post(url=f'{url}/app/test/', json={'dockerImage': docker_image,
                                                       'directories': list(directories),
                                                       'genericDirectory': generic_directory,
                                                       'isLocalRelay': is_local_relay,
                                                       'queryInterval': query_interval,
                                                       'downloadResults': download_results})
    if response.status_code == 200:
        return True, response.json()
    else:
        return False, response.content


def delete_test(url: str, test_id: str or int):
    response = http.delete(url=f'{url}/app/test/{test_id}/?delete=true')
    if response.status_code == 200:
        return True, response
    else:
        return False, response.json()


def stop_test(url: str, test_id: str or int):
    response = http.delete(url=f'{url}/app/test/{test_id}/?delete=false')
    if response.status_code == 200:
        return True, response.content
    else:
        return False, response.content


def get_tests(url: str):
    response = http.get(url=f'{url}/app/tests/')

    if response.status_code == 200:
        return True, response.json()
    else:
        return False, response.content


def delete_tests(url: str):
    response = http.delete(url=f'{url}/app/tests/')
    if response.status_code == 200:
        return True, response.content
    else:
        return False, response.content


def get_test(url: str, test_id: str or int):
    response = http.get(url=f'{url}/app/test/{test_id}/')

    if response.status_code == 200:
        return True, response.json()
    else:
        return False, response.json()


def get_traffic(url: str, test_id: str or int):
    response = http.get(url=f'{url}/app/test/{test_id}/traffic/')

    if response.status_code == 200:
        return True, response.json()
    else:
        return False, response.json()


def get_logs(url: str, test_id: str or int, instance_id: str or int, from_param: str):
    response = http.get(url=f'{url}/app/test/{test_id}/instance/{instance_id}/logs/?from={from_param}')
    if response.status_code == 200:
        return True, response.json()
    else:
        return False, response.json()
