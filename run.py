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

exp_data = []

# For each kernel, determine how many experiments they want to run and which benchmarks
for kernel in args.kernel:
    new_exp = {}
    new_exp.kernel = kernel
    new_exp.experiments = []

    exp_num = input("How many experiments would you like to run on this Kernel?:")
    for i in range(0, exp_num):
        benchmark_name = input("Which benchmark do you want to run?:")
        new_exp.experiments.append(benchmark_name)

experiments = ExperimentManager(exp_data)

if args.experiment is not None:
    current_kernel = int(args.experiment)

    if current_kernel > len(experiments.kernels):
        print("Invalid experiment number provided")
        exit()
else: 
    print(f"{len(experiments.kernels)} experiments to run:\n")
    current_kernel = -1

experiments.start(current_kernel)