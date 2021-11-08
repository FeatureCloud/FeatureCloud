import random
from time import sleep

from engine.app import App, AppState, app_state, Role

app = App()


def wrap_message(message, client):
    return f'{client}({message})'


@app_state(app, 'initial')
class InitialState(AppState):

    def register(self):
        self.register_transition('redirect', Role.BOTH)

    def run(self) -> str or None:
        if self.app.coordinator:
            client = random.choice(self.app.clients)
            message = wrap_message('Hello World!', self.app.id)
            sleep(10)
            self.send_data_to_participant(message, client)
        return 'redirect'


@app_state(app, 'redirect')
class InitialState(AppState):

    def register(self):
        self.register_transition('redirect', Role.BOTH)

    def run(self) -> str or None:
        message = self.await_data().decode()
        self.app.log(f'Received: {message}')

        if self.app.coordinator and message.startswith('DONE:'):
            return None

        if message.count('(') >= len(self.app.clients):
            self.app.log(f'Send to coordinator')
            self.send_data_to_coordinator(f'DONE:{message}')
        else:
            client = random.choice(self.app.clients)
            message = wrap_message(message, client)
            self.app.log(f'Send to {client}')
            self.send_data_to_participant(message, client)

        return 'redirect'
