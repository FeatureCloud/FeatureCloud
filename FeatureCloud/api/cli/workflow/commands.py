import click

@click.group("workflow")
def workflow() -> None:
    """Workflow related commands"""

@workflow.command('workflow')
@click.option('--controller-host', default='http://localhost:8000',
              help='Address of your running controller instance.',
              required=True)
@click.option('--wf-dir', default='.,.',
              help='workflow path',
              required=True)
@click.option('--channel', default='local',
              help='The communication channel to be used. Can be local or internet.',
              required=True)
@click.option('--query-interval', default=2,
              help='The interval after how many seconds the status call will be performed.',
              required=True)
def workflow(controller_host: str, wf_dir: str, channel: str, query_interval):
    # from
    pass
