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
        test_id = self.run_app('featurecloud.ai/dice_app')
        self.check_logs(test_id.strip())
        self.stop_app(test_id)
        self.stop_controller()
        self.create_new_app()

    def start_controller(self):
        output = subprocess.check_output(['featurecloud controller start'], shell=True)
        assert output.find(b'Started controller: fc-controller') > -1

    def run_app(self, app_name):
        output = subprocess.check_output([
            f'featurecloud test start --controller-host=http://localhost:8000 --client-dirs=. --generic-dir=. --app-image={app_name}'],
            shell=True)
        output = output.decode("utf-8")
        assert output.find('started') > -1
        output = output.replace('Test id=', '')
        return output.replace(' started', '')

    def check_logs(self, test_id):
        check_logs_cmd = f' featurecloud test logs --instance-id=0 --from-row=0 --controller-host="http://localhost:8000" --test-id={test_id}'
        output = subprocess.check_output([check_logs_cmd], shell=True)
        print(output)
        assert output.find(b'CRIT Supervisor is running as root') > -1

    def stop_app(self, test_id):
        output = subprocess.check_output([f'featurecloud  test stop --test-id={test_id}'], shell=True)
        assert output.find(b'stopped') > -1

    def stop_controller(self):
        output = subprocess.check_output(["featurecloud controller stop"], shell=True)
        assert output.find(b'Stopped controller(s): fc-controller') > -1

    def create_new_app(self):
        output = subprocess.check_output(["featurecloud app new my-blank-app --template-name=app-blank"],
                                         shell=True)
        assert output.find(b'Enjoy!') > -1
