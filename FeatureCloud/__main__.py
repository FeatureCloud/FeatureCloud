import click
from FeatureCloud.cli import cli
from FeatureCloud.controller import controller_management

@click.group("first-level")
def fc_cli() -> None:
    """FeatureCloud pip package"""




if __name__ == "__main__":
        fc_cli()
