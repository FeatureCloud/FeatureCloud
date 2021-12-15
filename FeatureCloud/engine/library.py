from distutils import dir_util

import yaml

from engine.app import AppState


class BlankState(AppState):

    def __init__(self, next_state: str = 'terminal'):
        super().__init__()
        self.next_state = next_state

    def register(self):
        if self.next_state:
            self.register_transition(self.next_state)

    def run(self):
        return self.next_state


class CopyState(BlankState):

    def __init__(self, next_state=None):
        super().__init__(next_state)

    def run(self):
        dir_util.copy_tree('/mnt/input/', '/mnt/output/')
        return super().run()


class ConfigState(BlankState):

    def __init__(self, next_state, section, config='config'):
        super().__init__(next_state)
        self.section = section
        self.config = config

    def run(self):
        if self.section:
            with open('/mnt/input/config.yml') as f:
                self.store(self.config, yaml.load(f, Loader=yaml.FullLoader)[self.section])
        return super().run()
