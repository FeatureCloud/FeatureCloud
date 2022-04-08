import click
from FeatureCloud.api.cli.test.commands import test
from FeatureCloud.api.cli.controller.commands import controller
from FeatureCloud.api.cli.app.commands import app


@click.group('first-level')
def fc_cli() -> None:
    """FeatureCloud pip package"""


fc_cli.add_command(test)
fc_cli.add_command(controller)
fc_cli.add_command(app)

if __name__ == "__main__":
    fc_cli()
