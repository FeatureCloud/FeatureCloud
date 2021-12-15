import argparse
import os
import subprocess
import sys

parser = argparse.ArgumentParser(description="For registering and testing your apps or using other apps, please visit "
                                             "our "
                                             "website: \n https://featurecloud.ai.\n And for more information about"
                                             " FeatureCloud architecture: \n"
                                             "The FeatureCloud AI Store for Federated Learning in Biomedicine and "
                                             "Beyond\n "
                                             "https://arxiv.org/abs/2105.05734 ",
                                 )
parser.add_argument("--echo", type=str, default=None, help="Get an input and print it!")
parser.add_argument('--delete', '--del', default=None, type=str, help='Delete a the given test run')
parser.add_argument('--info', type=str, default=None, help='Get details about the given test run')
parser.add_argument('--list', dest='list', help='List all test runs', action='store_true', default=False)
parser.add_argument('--logs', type=str, default=None, help='Get the logs of the given test runs')
parser.add_argument('--start', type=str, default=None, help='Start the given test run')
parser.add_argument('--stop', type=str, default=None, help='Stop the given test run')
parser.add_argument('--traffic', type=str, default=None, help='Show the traffic of a single test run')


def fc_command():
    args = parser.parse_args()
    python = sys.executable
    details = subprocess.check_output([python, '-m', 'pip', 'show', 'FeatureCloud'])
    path = None
    for pair in details.decode('utf-8').strip().split("\n"):
        if "location:" in pair.lower():
            path = pair.strip().split(":")[-1].strip()
    if path is None:
        raise KeyError("There is no location")

    cli = f"{path}/FeatureCloud/cli/cli.py"
    for k, v in vars(args).items():
        if v is not None:
            if k == 'echo':
                print(v)
            elif k == 'list':
                if v:
                    os.system(f'{python} {cli} {k}')
            else:

                os.system(f'{python} {cli} {k} {v}')
