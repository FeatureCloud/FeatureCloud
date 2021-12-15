import random
from time import sleep

from engine.app import AppState, app_state, Role


def wrap_message(message, client):
    return f'{client}({message})'


@app_state('initial')
class InitialState(AppState):

    def register(self):
        self.register_transition('redirect', Role.BOTH)

    def run(self):
        if self.is_coordinator:
            client = random.choice(self.clients)
            message = wrap_message('Hello World!', self.id)
            sleep(10)
            self.send_data_to_participant(message, client)
        return 'redirect'


@app_state('redirect')
class RedirectState(AppState):

    def register(self):
        self.register_transition('redirect', Role.BOTH)
        self.register_transition('terminal', Role.COORDINATOR)

    def run(self):
        message = self.await_data().decode()
        self.log(f'Received: {message}')

        if self.is_coordinator and message.startswith('DONE:'):
            return 'terminal'

        if message.count('(') >= len(self.clients):
            self.log(f'Send to coordinator')
            self.send_data_to_coordinator(f'DONE:{message}')
        else:
            client = random.choice(self.clients)
            message = wrap_message(message, client)
            self.log(f'Send to {client}')
            self.send_data_to_participant(message, client)

        return 'redirect'
