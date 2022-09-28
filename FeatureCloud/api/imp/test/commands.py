from FeatureCloud.api.imp.test import helper
from FeatureCloud.api.imp.test.api import controller
from FeatureCloud.api.imp.exceptions import ControllerOffline, FCException


def help():
    return (None, """For registering and testing your apps or using other apps, please visit 
          our 
          website: \n https://featurecloud.ai.\n And for more information about
           FeatureCloud architecture: \n
          The FeatureCloud AI Store for Federated Learning in Biomedicine and 
          Beyond\n 
          https://arxiv.org/abs/2105.05734 """)


def start(controller_host: str, client_dirs: str, generic_dir: str, app_image: str, channel: str, query_interval: str,
          download_results: str):
    if not controller.is_online(controller_host):
        raise ControllerOffline(controller_host)

    success, result = controller.start_test(controller_host,
                                            app_image,
                                            filter(None, client_dirs.split(',')),
                                            generic_dir,
                                            channel == 'local',
                                            query_interval,
                                            download_results)

    if success:
        return result['id']
    else:
        raise FCException(result['detail'])


def stop(controller_host: str, test_id: str or int):
    if not controller.is_online(controller_host):
        raise ControllerOffline(controller_host)

    success, result = controller.stop_test(controller_host, test_id)

    if success:
        return test_id
    else:
        raise FCException(result['detail'])


def delete(controller_host: str, test_id: str or int, del_all: str):
    if not controller.is_online(controller_host):
        raise ControllerOffline(controller_host)

    if test_id is not None and del_all is None:
        success, result = controller.delete_test(controller_host, test_id)

        if success:
            return test_id
        else:
            raise FCException(result['detail'])

    elif test_id is None and len(del_all) > 0:
        if del_all.lower() == 'all':
            success, result = controller.delete_tests(controller_host)

            if success:
                return 'all'
            else:
                raise FCException(result['detail'])
        else:
            raise FCException(f'Unsupported argument {del_all}')

    else:
        raise FCException('Wrong combination of parameters. To delete a single test use option --test-id. To delete all tests use the "all" argument.')


def list(controller_host: str, format: str = 'dataframe'):
    if not controller.is_online(controller_host):
        raise ControllerOffline(controller_host)

    success, result = controller.get_tests(controller_host)
    if success:
        if format == 'json':
            return result
        else:
            return helper.json_to_dataframe(result).set_index('id')
    else:
        raise FCException(result)


def info(controller_host: str, test_id: str or int, format: str = 'dataframe'):
    if not controller.is_online(controller_host):
        raise ControllerOffline(controller_host)

    success, result = controller.get_test(controller_host, test_id)
    if success:
        if format == 'json':
            return result
        else:
            return helper.json_to_dataframe(result, single_entry=True).set_index('id')
    else:
        raise FCException(result['detail'])


def traffic(controller_host: str, test_id: str or int, format: str):
    if not controller.is_online(controller_host):
        raise ControllerOffline(controller_host)

    success, result = controller.get_traffic(controller_host, test_id)
    if success:
        if format == 'json':
            return result
        else:
            return helper.json_to_dataframe(result)
    else:
        raise FCException(result['detail'])


def logs(controller_host: str, test_id: str or int, instance_id: str or int, from_param: str):
    if not controller.is_online(controller_host):
        raise ControllerOffline(controller_host)

    success, result = controller.get_logs(controller_host, test_id, instance_id, from_param)
    if success:
        return result["logs"]
    else:
        raise FCException(result['detail'])
