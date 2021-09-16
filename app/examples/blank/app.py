from engine.app import App, AppState, app_state

app = App()


@app_state(app, 'initial')
class InitialState(AppState):

    def run(self) -> str or None:
        return None
