import subprocess
import sys
from unittest import TestCase
from click.testing import CliRunner


class TestPipPackageTestCase(TestCase):

    def setUp(self):
        self.runner = CliRunner()
        # Install package
        # subprocess.run(['pip', 'install', 'dist/FeatureCloud-0.0.15.tar.gz'], capture_output=True)

    def test_pip(self):
        self.start_controller()
        self.run_dice_app()
        self.check_logs()
        self.stop_controller()
        self.create_new_app()

    def start_controller(self):
        # subprocess.run(['featurecloud controller start'], capture_output=True)
        subprocess.check_call(["featurecloud", "start", "controller"], stdout=subprocess.DEVNULL)

    def run_dice_app(self):
        pass

    def check_logs(self):
        pass

    def stop_controller(self):
        subprocess.run(['featurecloud controller stop'], capture_output=True)

    def create_new_app(self):
        pass
