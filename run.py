# CSC 450 Project 5: POC Kernel Compilation

import argparse
from experiment_manager import ExperimentManager

parser = argparse.ArgumentParser()
parser.add_argument('-k', '--kernel', action='append', nargs='+')
parser.add_argument('-e', '--experiment')
args = parser.parse_args()

if args.kernel is None:
    print("No kernels specified")
    exit()

print("Welcome to the Automated Experiment Execution Manager:\n")

experiments = ExperimentManager(args)

current_exp = None
if args.experiment is not None:
    current_exp = int(args.experiment)
    
    if current_exp >= len(experiments.exps):
        print("Invalid experiment number provided")
        exit()
else: 
    print(f"{len(experiments.exps)} experiments to run:\n")
    current_exp = -1

experiments.start(current_exp)


