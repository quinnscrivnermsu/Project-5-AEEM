# CSC 450 Project 5: POC Kernel Compilation

import argparse
from experiment_manager import ExperimentManager

parser = argparse.ArgumentParser()
parser.add_argument('-k', '--kernel', action='append', nargs='+')
parser.add_argument('-e', '--experiment')
args = parser.parse_args()

if args.kernel is None and args.experiment is None:
    print("No kernels specified")
    exit()

print("Welcome to the Automated Experiment Execution Manager:\n")

experiments = ExperimentManager(args)

if args.experiment is not None:
    current_kernel = int(args.experiment)

    if current_kernel > len(experiments.kernels):
        print("Invalid experiment number provided")
        exit()
else: 
    print(f"{len(experiments.kernels)} experiments to run:\n")
    current_kernel = -1

experiments.start(current_kernel)