import click
from importlib.metadata import version
import requests
from FeatureCloud.api.cli.test.commands import test
from FeatureCloud.api.cli.controller.commands import controller
from FeatureCloud.api.cli.app.commands import app

def get_latest_version(package_name):
    url = f'https://pypi.org/pypi/{package_name}/json'
    try:
        response = requests.get(url, timeout=3)
        response.raise_for_status()
        data = response.json()
        latest_version = data['info']['version']
        return latest_version
    except requests.exceptions.RequestException as e:
        return None

def get_warning_string():
    online_version =  get_latest_version("featurecloud")
    if online_version:
        online_version_list = online_version.split(".")
        local_version = version("featurecloud")
        local_version_list = local_version.split(".")
        for idx in range(min(len(online_version_list), len(local_version_list))):
            try:
                if int(online_version_list[idx]) > int(local_version_list[idx]):
                    click.echo(click.style(f'WARNING: your version is out of date. Your version is {local_version} but version {online_version} is available', fg='yellow', bold=True))
            except:
                return None
    return None

@click.version_option(version=version("featurecloud"))
@click.group('first-level', epilog=get_warning_string())
def fc_cli() -> None:
    """FeatureCloud pip package"""


fc_cli.add_command(test)
fc_cli.add_command(controller)
fc_cli.add_command(app)

if __name__ == "__main__":
    fc_cli()
