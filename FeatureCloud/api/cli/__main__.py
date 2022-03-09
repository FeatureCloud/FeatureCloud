import click
from FeatureCloud.api.cli.test.commands import test
from FeatureCloud.api.cli.workflow.commands import workflow
from FeatureCloud.api.cli.controller.commands import controller

@click.group('first-level')
def fc_cli() -> None:
    """FeatureCloud pip package"""

fc_cli.add_command(test)
fc_cli.add_command(workflow)
fc_cli.add_command(controller)

if __name__ == "__main__":
    fc_cli()
