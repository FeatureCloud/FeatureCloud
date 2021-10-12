import datetime
import threading
from time import sleep

from typing import Dict, List, Tuple


PARTICIPANT = (True, False)
COORDINATOR = (False, True)
BOTH = (True, True)


STATE_RUNNING = 'running'
STATE_ERROR = 'error'
STATE_ACTION = 'action_required'


def data_to_bytes(d):
    return


class App:

    def __init__(self):
        self.id = None
        self.coordinator = None
        self.clients = None

        self.thread = None

        self.status_available = False
        self.status_finished = False
        self.status_message = None
        self.status_progress = None
        self.status_state = None
        self.status_destination = None
        self.status_smpc = None

        self.data_incoming = []
        self.data_outgoing = []

        self.default_smpc = {'operation': 'add', 'serialization': 'json', 'shards': 0, 'range': 0}

        self.current_state: AppState or None = None
        self.states: Dict[str, AppState] = {}
        self.transitions: Dict[str, Tuple[AppState, AppState, bool, bool]] = {}  # name => (source, target, participant, coordinator)
        self.transition_log: List[Tuple[datetime.datetime, str]] = []

        self.internal = {}

    def handle_setup(self, client_id, coordinator, clients):
        # This method is called once upon startup and contains information about the execution context of this instance
        self.id = client_id
        self.coordinator = coordinator
        self.clients = clients

        self.log(f'id: {self.id}')
        self.log(f'coordinator: {self.coordinator}')
        self.log(f'clients: {self.clients}')

        self.current_state = self.states.get('initial')

        if not self.current_state:
            raise RuntimeError('initial state not found')

        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def run(self):
        while True:
            self.log(f'state: {self.current_state.name}')
            transition = self.current_state.run()
            if not transition:
                self.status_progress = 1.0
                self.log(f'done')
                sleep(10)
                self.status_finished = True
                return
            self.log(f'transition: {transition}')
            self.transition(f'{self.current_state.name}_{transition}')
            sleep(1)

    def register(self):
        for s in self.states:
            state = self.states[s]
            state.register()

    def handle_incoming(self, data, client):
        # This method is called when new data arrives
        self.data_incoming.append((data.read(), client))

    def handle_outgoing(self):
        # This method is called when data is requested
        if len(self.data_outgoing) == 0:
            return None
        data = self.data_outgoing[0]
        self.data_outgoing = self.data_outgoing[1:]
        if len(self.data_outgoing) == 0:
            self.status_available = False
            self.status_destination = None
            self.status_smpc = None
        else:
            self.status_available = True
            self.status_destination = self.data_outgoing[0][1]
            self.status_smpc = self.default_smpc if self.data_outgoing[0][2] else None
        return data[0]

    def _register_state(self, name, state, participant, coordinator, **kwargs):
        if self.transitions.get(name):
            raise RuntimeError(f'state {name} already exists')

        si = state(**kwargs)
        si.app = self
        si.name = name
        si.participant = participant
        si.coordinator = coordinator
        self.states[si.name] = si

    def register_transition(self, name: str, source: str, target: str, participant=True, coordinator=True):
        if not participant and not coordinator:
            raise RuntimeError('either participant or coordinator must be True')

        if self.transitions.get(name):
            raise RuntimeError(f'transition {name} already exists')

        source_state = self.states.get(source)
        if not source_state:
            raise RuntimeError(f'source state {source} not found')
        if participant and not source_state.participant:
            raise RuntimeError(f'source state {source} not accessible for participants')
        if coordinator and not source_state.coordinator:
            raise RuntimeError(f'source state {source} not accessible for the coordinator')

        target_state = self.states.get(target)
        if not target_state:
            raise RuntimeError(f'target state {target} not found')
        if participant and not target_state.participant:
            raise RuntimeError(f'target state {target} not accessible for participants')
        if coordinator and not target_state.coordinator:
            raise RuntimeError(f'target state {target} not accessible for the coordinator')

        self.transitions[name] = (source_state, target_state, participant, coordinator)

    def transition(self, name):
        transition = self.transitions.get(name)
        if not transition:
            raise RuntimeError(f'transition {name} not found')
        if transition[0] != self.current_state:
            raise RuntimeError(f'current state unequal to source state')
        if not transition[2] and not self.coordinator:
            raise RuntimeError(f'cannot perform transition {name} as participant')
        if not transition[3] and self.coordinator:
            raise RuntimeError(f'cannot perform transition {name} as coordinator')

        self.transition_log.append((datetime.datetime.now(), name))
        self.current_state = transition[1]

    def log(self, msg):
        print(msg, flush=True)


class AppState:

    def __init__(self):
        self.app = None
        self.name = None
        self.participant = None
        self.coordinator = None

    def register(self):
        pass

    def run(self) -> str or None:
        pass

    def register_transition(self, target: str, role=BOTH, name: str or None = None):
        if not name:
            name = target
        participant, coordinator = role
        self.app.register_transition(f'{self.name}_{name}', self.name, target, participant, coordinator)

    def gather_data(self):
        return self.await_data(len(self.app.clients), unwrap=False)

    def await_data(self, n: int = 1, unwrap: bool = True):
        while True:
            if len(self.app.data_incoming) >= n:
                data = self.app.data_incoming[:n]
                self.app.data_incoming = self.app.data_incoming[n:]
                if unwrap and n == 1:
                    return data[0][0]
                else:
                    return data[0]
            sleep(1)

    def send_data_to_participant(self, data, destination):
        if destination == self.app.id:
            self.app.data_incoming.append((data, self.app.id))
        else:
            self.app.data_outgoing.append((data, False, destination))
            self.app.status_destination = destination
            self.app.status_smpc = None
            self.app.status_available = True

    def send_data_to_coordinator(self, data, send_to_self=True, use_smpc=False):
        if self.app.coordinator and not use_smpc:
            if send_to_self:
                self.app.data_incoming.append((data, self.app.id))
        else:
            self.app.data_outgoing.append((data, use_smpc, None))
            self.app.status_destination = None
            self.app.status_smpc = self.app.default_smpc if use_smpc else None
            self.app.status_available = True

    def broadcast_data(self, data, send_to_self=True):
        if not self.app.coordinator:
            raise RuntimeError('only the coordinator can broadcast data')
        self.app.data_outgoing.append((data, False, None))
        self.app.status_destination = None
        self.app.status_smpc = None
        self.app.status_available = True
        if send_to_self:
            self.app.data_incoming.append((data, self.app.id))

    def update(self, message=None, progress=None, state=None):
        if message and len(message) > 40:
            raise RuntimeError('message is too long')
        if progress is not None and (progress < 0 or progress > 1):
            raise RuntimeError('progress must be between 0 and 1')
        if state is not None and state != STATE_RUNNING and state != STATE_ERROR and state != STATE_ACTION:
            raise RuntimeError('invalid state')
        self.app.status_message = message
        self.app.status_progress = progress
        self.app.status_state = state


def app_state(app: App, name: str, role=BOTH, **kwargs):
    participant, coordinator = role
    if not participant and not coordinator:
        raise RuntimeError('either participant or coordinator must be True')

    def func(state_class):
        app._register_state(name, state_class, participant, coordinator, **kwargs)
        return state_class

    return func
