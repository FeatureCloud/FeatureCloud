import random
from time import sleep

from engine.app import App, AppState, app_state, BOTH, COORDINATOR, PARTICIPANT

app = App()


@app_state(app, 'initial', BOTH)
class InitialState(AppState):
    """
    This is the initial state from which we directly transition to the dice state.
    """

    def register(self):
        self.register_transition('throw_die', BOTH)  # We need to declare which states we can transition to from here

    def run(self) -> str or None:
        sleep(5)
        return 'throw_die'


@app_state(app, 'throw_die', BOTH)
class DieState(AppState):
    """
    Here we throw the die and send the data away.
    """

    def register(self):
        self.register_transition('aggregate', COORDINATOR)
        self.register_transition('obtain', PARTICIPANT)

    def run(self) -> str or None:
        d = random.randint(1, 6)
        self.app.log(f'threw a {d}')

        self.send_to_coordinator(f'{d}')

        if self.app.coordinator:
            return 'aggregate'
        else:
            return 'obtain'


@app_state(app, 'aggregate', COORDINATOR)
class AggregateState(AppState):
    """
    Here we aggregate the values and broadcast them.
    """

    def register(self):
        self.register_transition('obtain', COORDINATOR)

    def run(self) -> str or None:
        dies = self.gather_data()
        s = sum([int(d) for d in dies])
        self.broadcast(f'{s}')
        return 'obtain'


@app_state(app, 'obtain', BOTH)
class ObtainState(AppState):

    def run(self) -> str or None:
        s = self.await_data()
        self.app.log(f'sum is {s}')
        return None
