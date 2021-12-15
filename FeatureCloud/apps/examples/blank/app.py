from engine.app import AppState, app_state


# This is the first (initial) state all app instances are in at the beginning
# By calling it 'initial' the FeatureCloud template engine knows that this state is the first one to go into automatically at the beginning
@app_state('initial')  # The first argument is the name of the state ('initial'), the second specifies which roles are allowed to have this state (here BOTH)
class InitialState(AppState):

    def register(self):
        self.register_transition('terminal')  # We declare that 'terminal' is accessible from the 'initial' state

    def run(self):
        return 'terminal'  # This means we are done. If the coordinator transitions into the 'terminal' state, the whole computation will be shut down
