import click
import importlib
import os
import sys


@click.group("workflow")
def workflow() -> None:
    """Workflow related commands"""


@workflow.command('start')
@click.option('--controller-host', default='http://localhost:8000',
              help='Address of your running controller instance.',
              required=True)
@click.option('--wf-dir', default='',
              help='path to directory containing the workflow',
              required=True)
@click.option('--wf-file', default='example_wf',
              help='python file including the workflow',
              required=True)
@click.option('--channel', default='local',
              help='The communication channel to be used. Can be local or internet.',
              required=True)
@click.option('--query-interval', default=1,
              help='The interval after how many seconds the status call will be performed.',
              required=True)
@click.pass_context
def start_workflow(ctx: click.Context, controller_host: str, wf_dir: str, wf_file: str, channel: str,
                   query_interval: str):
    profile = "featurecloud"
    if ctx.obj:
        profile = ctx.obj.get("profile", "featurecloud")
    prev = os.environ.get("FC_CLI_PROFILE")
    sys.path.append(wf_dir)
    workflow_class = importlib.import_module(wf_file)
    try:
        os.environ["FC_CLI_PROFILE"] = profile
        wf = workflow_class.WorkFlow(controller_host=controller_host, channel=channel, query_interval=query_interval)
        wf.register_apps()
        wf.run()
    finally:
        if prev is None:
            os.environ.pop("FC_CLI_PROFILE", None)
        else:
            os.environ["FC_CLI_PROFILE"] = prev
