import os, stat, fileinput, re
from collections import defaultdict
from subprocess import PIPE, DEVNULL

PROGRAM_DIR = os.getcwd()
SCRIPTS_PATH = PROGRAM_DIR + '/scripts'

class ExperimentManager:
    exps = defaultdict(list)

    def __init__(self, args):
        for element in args.kernel:
            for experiment in element:
                if os.path.exists(experiment):
                    self.exps[experiment] = []

    def setup_environment(self, experiment):
        print(f"Setting up environment for Experiment {experiment}...")

    def start(self):
        print(f"{len(self.exps.keys())} experiments to run:\n")

        for experiment in self.exps.keys():
            print(f"Experiment {experiment}:")

            self.setup_environment(experiment)

            # Start the compile and track output.
    
            print("Starting Experiment...")
            
            # @TODO: Run the GAP Benchmark suite here based on user input.

            print("Experiment successful!")
            

            # @TODO: Store it in the cloud server, after visualization