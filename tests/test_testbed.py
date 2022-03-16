import json
import os
from unittest import TestCase
import api.controller as controller
from click.testing import CliRunner
from cli import test


class TestBedTestCase(TestCase):

    def setUp(self):
        self.runner = CliRunner()
        try:
            self.controller_url = os.environ["CONTROLLER_URL"]
        except KeyError:
            self.controller_url = "http://localhost:8000"

        result = controller.is_online(url=self.controller_url)
        print(f'Controller online: {result} on {self.controller_url}')
        assert result is True

    def tearDown(self):
        self.runner.invoke(test, ['delete', '--controller-host', self.controller_url, '--test-id', 1])
        result = self.runner.invoke(test, ['list', '--controller-host', self.controller_url])
        assert result.exit_code == 0
        assert result.output == 'No tests available.\n'

    def test(self):
        print("Test list")
        result = self.runner.invoke(test, ['list', '--controller-host', self.controller_url])
        assert result.exit_code == 0
        assert result.output == 'No tests available.\n'
        print("Successful.")

        print("Test start")
        result = self.runner.invoke(test, ['start', '--controller-host', self.controller_url])
        assert result.exit_code == 0
        print(result.output)
        assert "{'id': 1}" in result.output or "1" in result.output
        print("Successful.")

        print("Test info")
        result = self.runner.invoke(test, ['info', '--controller-host', self.controller_url, '--test-id', 1, '--format',
                                           'json'])
        assert result.exit_code == 0
        print(result.output)
        assert "'status': 'running'" in json.dumps(result.output)
        print("Successful.")

        print("Test logs")
        result = self.runner.invoke(test,
                                    ['logs', '--controller-host', self.controller_url, '--test-id', 1, '--instance-id',
                                     0])
        assert result.exit_code == 0
        assert 'Supervisor is running as root.' in result.output
        print("Successful.")

        print("Test traffic")
        result = self.runner.invoke(test,
                                    ['traffic', '--controller-host', self.controller_url, '--test-id', 1, '--format',
                                     'json'])
        assert result.exit_code == 0
        print(result.output)
        assert '[]' in result.output
        print("Successful.")

        print("Test stop")
        result = self.runner.invoke(test, ['stop', '--controller-host', self.controller_url, '--test-id', 1])
        assert result.exit_code == 0
        print(result.output)
        print("Successful.")

        print("Test info")
        result = self.runner.invoke(test, ['info', '--controller-host', self.controller_url, '--test-id', 1, '--format',
                                           'json'])
        assert result.exit_code == 0
        print(result.output)
        assert "'status': 'stopped'" in json.dumps(result.output)
        print("Successful.")

        print("Test list")
        result = self.runner.invoke(test, ['list', '--controller-host', self.controller_url, '--format', 'json'])
        assert result.exit_code == 0
        print(result.output)
        assert "'id': 1" in json.dumps(result.output)
        print("Successful.")

        print("All tests completed sucessfully.")
