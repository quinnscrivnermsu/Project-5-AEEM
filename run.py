# CSC 450 Project 5: POC Kernel Compilation
import os
import argparse
from experiment_manager import ExperimentManager

parser = argparse.ArgumentParser()
parser.add_argument('-k', '--kernel', action='append', nargs='+')
parser.add_argument('-e', '--experiment')
args = parser.parse_args()



#if args.kernel is None and args.experiment is None:
#    print("No kernels specified")
#    exit()

print("Welcome to the Automated Experiment Execution Manager:\n")

kernel_num = input("Input How Many Kernels Will Be Used: ")
exp_data = []
kernel_info = []
for number in kernel_num:
    kernel_loc = input("Input Kernel Path: ")
    if os.path.exists(kernel_loc):
        exp_data.append(kernel_loc)
        kernel_info.append(kernel_loc)
        #args.kernel = kernel_loc
    else:
        print("Path does not exist.")
        exit()


# For each kernel, determine how many experiments they want to run and which benchmarks
for kernel in kernel_info:
    new_exp = {}
    new_exp["kernel"] = kernel
    new_exp["experiments"] = []

    exp_num = int(input("How many experiments would you like to run on this Kernel?:"))
    for i in range(0, exp_num):
        benchmark_name = input("Which benchmark do you want to run?:")
        new_exp['experiments'].append(benchmark_name)

experiments = ExperimentManager(exp_data)

if args.experiment is not None:
    current_kernel = int(args.experiment)

    if current_kernel > len(experiments.kernels):
        print("Invalid experiment number provided")
        exit()
else: 
    print(f"{len(experiments.kernels)} experiments to run:\n")
    current_kernel = -1

with open("text.txt", "w") as file:
    for value in exp_data:
        file.write("".join(value) + "\n")

experiments.start(current_kernel)