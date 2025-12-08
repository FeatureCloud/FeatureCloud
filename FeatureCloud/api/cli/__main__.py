import sys
import click
from importlib.metadata import version
import requests

from FeatureCloud.api.cli.test.commands import test
from FeatureCloud.api.cli.controller.commands import controller
from FeatureCloud.api.cli.app.commands import app


def get_latest_version(package_name: str):
    url = f"https://pypi.org/pypi/{package_name}/json"
    try:
        response = requests.get(url, timeout=3)
        response.raise_for_status()
        data = response.json()
        latest_version = data["info"]["version"]
        return latest_version
    except requests.exceptions.RequestException:
        return None


def get_warning_string():
    online_version = get_latest_version("featurecloud")
    if online_version:
        online_version_list = online_version.split(".")
        local_version = version("featurecloud")
        local_version_list = local_version.split(".")
        for idx in range(min(len(online_version_list), len(local_version_list))):
            try:
                if int(online_version_list[idx]) > int(local_version_list[idx]):
                    click.echo(
                        click.style(
                            f"WARNING: your version is out of date. "
                            f"Your version is {local_version} but "
                            f"version {online_version} is available",
                            fg="yellow",
                            bold=True,
                        )
                    )
                    break
            except Exception:
                return None
    return None


def _init_ctx_profile(ctx: click.Context, default_profile: str) -> None:
    """Initialize click context object with a default profile."""
    ctx.ensure_object(dict)
    # Only set if not already set, so nested calls won't overwrite
    ctx.obj.setdefault("profile", default_profile)


# ---------- FeatureCloud CLI root ----------

@click.version_option(version=version("featurecloud"))
@click.group("first-level", epilog=get_warning_string())
@click.pass_context
def fc_cli(ctx: click.Context) -> None:
    """FeatureCloud CLI."""
    # Default profile for 'featurecloud' entry points
    _init_ctx_profile(ctx, default_profile="featurecloud")


fc_cli.add_command(test)
fc_cli.add_command(controller)
fc_cli.add_command(app)


# ---------- CVDLink CLI root ----------

@click.version_option(version=version("featurecloud"))
@click.group("first-level", epilog=get_warning_string())
@click.pass_context
def cvdlink_cli(ctx: click.Context) -> None:
    """CVDLink CLI (based on FeatureCloud)."""
    # Default profile for 'cvdlink' entry points
    _init_ctx_profile(ctx, default_profile="cvdlink")


cvdlink_cli.add_command(test)
cvdlink_cli.add_command(controller)
cvdlink_cli.add_command(app)


if __name__ == "__main__":
    # Fallback if someone runs `python -m FeatureCloud.api.cli.__main__`
    # Default to FeatureCloud behavior.
    fc_cli()
