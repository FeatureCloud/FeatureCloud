import subprocess
from unittest import TestCase


class TestPipPackageTestCase(TestCase):

    def setUp(self):
        # Install package. This should happen in CICD pipeline prior running these tests
        # try:
        #     output = subprocess.check_output(['pip install featurecloud'], shell=True)
        #     assert output.find(b'Successfully installed FeatureCloud') > -1
        # except subprocess.CalledProcessError as e:
        #     print(e.returncode)
        #     print(e.output)
        pass

    def test_pip(self):
        self.start_controller()
        self.run_dice_app()
        test_id = self.run_test_app()
        self.check_logs(test_id)
        self.stop_test_app(test_id)
        self.stop_controller()
        self.create_new_app()

    def start_controller(self):
        try:
            output = subprocess.check_output(['featurecloud controller start'], shell=True)
            assert output.find(b'Started controller: fc-controller') > -1
        except subprocess.CalledProcessError as e:
            print(e.returncode)
            print(e.output)

    def run_dice_app(self):
        # TODO: enable this when dice app becomes available on featurecloud.ai
        # try:
        #     output = subprocess.check_output([
        #         'featurecloud test start --controller-host=http://localhost:8000 --client-dirs=. --generic-dir=. --app-image=featurecloud.ai/dice_app'],
        #         shell=True)
        #     output = output.decode("utf-8")
        #     assert output.find('started') > -1
        #     output = output.replace('Test id=', '')
        #     return output.replace(' started', '')
        # except subprocess.CalledProcessError as e:
        #     print(e.returncode)
        #     print(e.output)
        pass

    def run_test_app(self):
        try:
            output = subprocess.check_output([
                'featurecloud test start --controller-host=http://localhost:8000 --client-dirs=. --generic-dir=. --app-image=featurecloud.ai/test_app'],
                shell=True)
            output = output.decode("utf-8")
            assert output.find('started') > -1
            output = output.replace('Test id=', '')
            return output.replace(' started', '')
        except subprocess.CalledProcessError as e:
            print(e.returncode)
            print(e.output)

    def check_logs(self, test_id):
        try:
            output = subprocess.check_output([
                                                 f' featurecloud test logs --test-id={test_id}  --controller-host=http://localhost:8000 --instance-id=0 --from-param=0'],
                                             shell=True)
            assert output.find(b'Sent status') > -1
        except subprocess.CalledProcessError as e:
            print(e.returncode)
            print(e.output)

    def stop_test_app(self, test_id):
        try:
            output = subprocess.check_output([f'featurecloud  test stop --test-id={test_id}'], shell=True)
            assert output.find(b'stopped') > -1
        except subprocess.CalledProcessError as e:
            print(e.returncode)
            print(e.output)

    def stop_controller(self):
        try:
            output = subprocess.check_output(["featurecloud controller stop"], shell=True)
            assert output.find(b'Stopped controller(s): fc-controller') > -1
        except subprocess.CalledProcessError as e:
            print(e.returncode)
            print(e.output)

    def create_new_app(self):
        try:
            output = subprocess.check_output(["featurecloud app new my-blank-app --template-name=app-blank"],
                                             shell=True)
            assert output.find(b'Ready to develop! Enjoy!') > -1
        except subprocess.CalledProcessError as e:
            print(e.returncode)
            print(e.output)
