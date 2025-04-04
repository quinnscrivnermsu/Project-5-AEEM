# CSC 450 Project 5: Automated Experiment Execution Manager

import os, argparse
from experiment_manager import ExperimentManager

parser = argparse.ArgumentParser()
parser.add_argument('-k', '--kerneltorun', action='append', nargs='+')
args = parser.parse_args()

print("Welcome to the Automated Experiment Execution Manager:\n")

manager = ExperimentManager()

if args.kerneltorun is None:
    # Continously ask for how many kernels will be used until kernel_num is valid.
    while True:
        try:
            kernel_num =  int(input("Input How Many Kernels Will Be Used: "))
        except ValueError:
            print("Invalid input. Please try again.")
            continue
        else:
            break

    # Loop through the amount of kernels and ask for the path and check if it exists
    kernel_info = []
    for number in range(0,kernel_num):
        while True:
            kernel_loc = input(f"Input Kernel {number + 1} Path: ")
            if os.path.exists(kernel_loc):
                kernel_loc = kernel_loc.replace('/boot/', '') # Replace /boot/ in kernel name
                kernel_info.append(kernel_loc)
                break
            else:
                print("Path does not exist. Please try again.")
                continue

    exp_data = []

    # For each kernel, determine how many experiments they want to run and which benchmarks
    for kernel in kernel_info:
        new_exp = {}
        new_exp["kernel"] = kernel
        new_exp["experiments"] = []

        exp_num = int(input(f"How many experiments would you like to run for Kernel ({kernel})?: "))
        for i in range(0, exp_num):
            command = input(f"Please enter the command you would like to run at position {i + 1}: ")
            new_exp['experiments'].append(command)

        exp_data.append(new_exp)

    manager.load_experiment_data(exp_data)
    manager.write_benchmarks_to_file()
    manager.start()
else:
    # Open the kernel text file, and run each benchmark and store the results.
    manager.run_benchmarks(args.kerneltorun[0][0])