# CSC 450 Project 5: POC Kernel Compilation

import argparse
from experiment_manager import ExperimentManager

parser = argparse.ArgumentParser()
parser.add_argument('-k', '--kernel', action='append', nargs='+')
parser.add_argument('-t', '--threads')
args = parser.parse_args()

if args.kernel is None:
    print("No kernels specified")
    exit()

print("Welcome to the Automated Experiment Execution Manager:\n")

experiments = ExperimentManager(args)
experiments.start()
