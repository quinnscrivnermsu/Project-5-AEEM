# CSC 450 Project 5: POC Kernel Compilation

import argparse
from kernel_compiler import KernelCompiler

parser = argparse.ArgumentParser()
parser.add_argument('-k', '--kernel', action='append', nargs='+')
parser.add_argument('-t', '--threads')
args = parser.parse_args()

if args.kernel is None:
    print("No kernels specified")
    exit()

if args.threads is None:
    args.threads = 4

print("Welcome to the Automated Experiment Execution Manager:\n")

compiler = KernelCompiler(args)
compiler.start(args.threads)