from sys import exit
from FeatureCloud.api.imp.test.api import controller
from FeatureCloud.api.imp.test import helper


def help():
    return (None, """For registering and testing your apps or using other apps, please visit 
          our 
          website: \n https://featurecloud.ai.\n And for more information about
           FeatureCloud architecture: \n
          The FeatureCloud AI Store for Federated Learning in Biomedicine and 
          Beyond\n 
          https://arxiv.org/abs/2105.05734 """)


def start(controller_host: str, client_dirs: str, generic_dir: str, app_image: str, channel: str, query_interval,
          download_results: str):
    if not controller.is_online(controller_host):
        msg = f'No controller online on {controller_host}. Exiting.'
        return (None, msg)

    success, result = controller.start_test(controller_host,
                                            app_image,
                                            filter(None, client_dirs.split(',')),
                                            generic_dir,
                                            channel == 'local',
                                            query_interval,
                                            download_results)

    if success:
        msg = result['id']
        return (result['id'], msg)
    else:
        msg = result
        return (None. msg)


def stop(controller_host: str, test_id: str or int):
    if not controller.is_online(controller_host):
        msg = f'No controller online on {controller_host}.'
        return (None, msg)

    success, result = controller.stop_test(controller_host, test_id)
    if not success:
        msg = result
        return (None, msg)

def delete(controller_host: str, test_id: str or int, what: tuple):
    if not controller.is_online(controller_host):
        msg = f'No controller online on {controller_host}.'
        return (None, msg)

    if test_id is not None and len(what) == 0:
        success, result = controller.delete_test(controller_host, test_id)

        if not success:
            msg = result['detail']
            return (None, msg)

    elif test_id is None and len(what) > 0:
        if what[0].lower() == 'all':
            success, result = controller.delete_tests(controller_host)

            if not success:
                msg = result['detail']
                return (None, msg)
        else:
            msg = f'Unsupported argument {what[0]}'
            return (None, msg)

    else:
        msg = 'Wrong combination of parameters. To delete a single test use option --test-id. To delete all tests use the "all" argument.'
        return (None, msg)


def list(controller_host: str, format: str):
    if not controller.is_online(controller_host):
        msg = f'No controller online on {controller_host}. Exiting.'
        return (None, msg)

    success, result = controller.get_tests(controller_host)
    if success:
        if len(result) == 0:
            msg = 'No tests available.'
            return (None, msg)
        if format == 'json':
            msg = result
            return (result, msg)
        elif format == 'dataframe':
            df = helper.json_to_dataframe(result).set_index('id')
            msg = df.to_string()
            return (df, msg)
        else:
            msg = f'Format {format} not available. Returning json.'
            msg += result
            return (result, msg)
    else:
        msg = result
        return (None, msg)


def info(controller_host: str, test_id: str or int, format: str):
    if not controller.is_online(controller_host):
        msg = f'No controller online on {controller_host}. Exiting.'
        return (None, msg)

    success, result = controller.get_test(controller_host, test_id)
    if success:
        if format == 'json':
            msg = result
            return (result, msg)
        elif format == 'dataframe':
            df = helper.json_to_dataframe(result, single_entry=True).set_index('id')
            msg = df.to_string()
            return (df, msg)
        else:
            msg = f'Format {format} not available. Returning json.'
            return (result, msg)
    else:
        msg = result['detail']
        return (None, msg)


def traffic(controller_host: str, test_id: str or int, format: str):
    if not controller.is_online(controller_host):
        msg = f'No controller online on {controller_host}. Exiting.'
        return (None, msg)

    success, result = controller.get_traffic(controller_host, test_id)
    if success:
        if format == 'json':
            msg = result
            return (result, msg)
        elif format == 'dataframe':
            df = helper.json_to_dataframe(result)
            msg = df.to_string()
            return (df, msg)
        else:
            msg = f'Format {format} not available. Returning json.'
            return (result, msg)
    else:
        msg = result['detail']
        return (None, msg)


def logs(controller_host: str, test_id: str or int, instance_id: str or int, from_param: str):
    if not controller.is_online(controller_host):
        msg = f'No controller online on {controller_host}. Exiting.'
        return (None, msg)

    success, result = controller.get_logs(controller_host, test_id, instance_id, from_param)
    if success:
        msg = ""
        for line in result["logs"]:
            msg += '\n' + line
        return (result, msg)
    else:
        msg = result['detail']
        return (None, msg)
