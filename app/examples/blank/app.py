from engine.app import App, AppState, app_state

# This is the app instance, which holds various values and is used by the app states below
# You shouldn't access this app instance directly, just ignore it for now
app = App()


# This is the first (initial) state all app instances are in at the beginning
# By calling it 'initial' the FeatureCloud template engine knows that this state is the first one to go into automatically at the beginning
@app_state(app, 'initial')  # The first argument is the name of the state ('initial'), the second specifies which roles are allowed to have this state (here BOTH)
class InitialState(AppState):

    def run(self) -> str or None:
        return None  # This means we are done. If the coordinator transitions into the `None` state, the whole computation will be shut down
