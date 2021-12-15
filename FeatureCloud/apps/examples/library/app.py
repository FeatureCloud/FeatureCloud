from engine.app import app_state
from engine.library import BlankState, CopyState, ConfigState


@app_state('initial', next_state='copy')
class InitialState(BlankState):
    pass


@app_state('copy', next_state='config')
class CopyState(CopyState):
    pass


@app_state('config', section='my_app', config='my_config', next_state='display')
class ConfigState(ConfigState):
    pass


@app_state('display', next_state='terminal')
class InitialState(BlankState):

    def run(self):
        config = self.load('my_config')
        self.log(f'Config: {config}')
