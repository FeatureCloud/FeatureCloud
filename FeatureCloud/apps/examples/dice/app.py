"""
This demo implementation works as follows:
1. Each participant throws a die (random number between 1 and 6)
2. They then send their thrown number to the coordinator
3. The coordinator aggregates all values (calculates the sum)
4. The coordinator broadcasts the sum to all participants
5. The participants print the received sum to the log messages
"""

#  Imports
import random
from time import sleep

from engine.app import AppState, app_state, Role, SMPCOperation


# Here we can toggle if we want to use Secure Multi-Party Computation (SMPC)
# This is a custom flag we are only using internally in the implementation below
USE_SMPC = True


# This is the first (initial) state all app instances are in at the beginning
# By calling it 'initial' the FeatureCloud template engine knows that this state is the first one to go into automatically at the beginning
@app_state('initial', Role.BOTH)  # The first argument is the name of the state ('initial'), the second specifies which roles are allowed to have this state (here BOTH)
class InitialState(AppState):
    """
    This is the initial state from which we directly transition to the dice state.
    """

    def register(self):
        # We need to declare which states are accessible from this state (the 'initial' state)
        # If we don't declare them, we cannot transition to them later
        self.register_transition('throw_die', Role.BOTH)  # We declare that 'throw_die' is accessible from the 'initial' state, for both the coordinator and the participants (BOTH)

    def run(self) -> str or None:
        self.update(progress=0.1)  # We update the progress, so that the FeatureCloud system can display it on the frontend
        sleep(5)
        return 'throw_die'  # By returning a string, we specify which state we want to go into next (here 'throw_die'). It has to match another state string (see below).


@app_state('throw_die', Role.BOTH)
class DieState(AppState):
    """
    Here we throw the die and send the data away.
    """

    def register(self):
        self.register_transition('aggregate', Role.COORDINATOR)
        self.register_transition('obtain', Role.PARTICIPANT)

    def run(self) -> str or None:
        self.update(progress=0.25)
        d = random.randint(1, 6)
        self.log(f'threw a {d}')  # This is how we can log a message for debugging purposes
        self.configure_smpc(exponent=6, operation=SMPCOperation.ADD)  # SMPC needs an exponent to transform numbers (here 6) into fixed-point values and an operation (either 'add' or 'multiply')
        self.send_data_to_coordinator(d, use_smpc=USE_SMPC)  # Here, we send data to the coordinator. `use_smpc` specifies whether we want to use SMPC

        if self.is_coordinator:
            return 'aggregate'
        else:
            return 'obtain'


@app_state('aggregate', Role.COORDINATOR)
class AggregateState(AppState):
    """
    Here we aggregate the values and broadcast them.
    """

    def register(self):
        self.register_transition('obtain', Role.COORDINATOR)

    def run(self) -> str or None:
        self.update(progress=0.6)

        # `aggregate_data` either takes the already aggregated SMPC value or aggregates them internally using the specified operation (here 'add')
        s = self.aggregate_data(SMPCOperation.ADD, use_smpc=USE_SMPC)

        self.broadcast_data(s)  # `broadcast_data` sends the data to all other participants, including the coordinator instance (unless `send_to_self` is set `False`)
        return 'obtain'


@app_state('obtain', Role.BOTH)
class ObtainState(AppState):
    """
    Here we print the received sum.
    """

    def register(self):
        self.register_transition('terminal')

    def run(self) -> str or None:
        self.update(progress=0.9)
        s = self.await_data()
        self.log(f'sum is {s}')
        self.update(message=f'obtained sum {s}')
        return 'terminal'  # This means we are done. If the coordinator transitions into the 'terminal' state, the whole computation will be shut down
