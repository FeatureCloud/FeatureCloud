from engine.app import App, app_state
from engine.library import BlankState, CopyState, ConfigState

# This is the app instance, which holds various values and is used by the app states below
# You shouldn't access this app instance directly, just ignore it for now

app = App()


@app_state(app, 'initial', next_state='copy')
class InitialState(BlankState):
    pass


@app_state(app, 'copy', next_state='config')
class CopyState(CopyState):
    pass


@app_state(app, 'config', section='my_app', config='my_config', next_state='display')
class ConfigState(ConfigState):
    pass


@app_state(app, 'display', next_state='terminal')
class InitialState(BlankState):

    def run(self):
        config = self.app.internal['my_config']
        self.app.log(f'Config: {config}')
