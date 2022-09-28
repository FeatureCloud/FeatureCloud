from FeatureCloud.api.imp.test import commands
from functools import partial


class Controller:
    def __init__(self, controller_host: str, channel: str, query_interval: str):
        self.controller_host = controller_host
        self.channel = channel
        self.query_interval = query_interval
        self.start = partial(commands.start, controller_host=controller_host, channel=channel,
                             query_interval=query_interval)
        self.stop = partial(commands.stop, controller_host=controller_host)
        self.delete = partial(commands.delete, controller_host=controller_host)
        self.list = partial(commands.list, controller_host=controller_host)
        self.traffic = partial(commands.traffic, controller_host=controller_host)
        self.logs = partial(commands.logs, controller_host=controller_host)
        self.info = partial(commands.info, controller_host=controller_host)
