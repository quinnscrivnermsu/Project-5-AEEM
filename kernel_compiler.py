import os, stat
from collections import defaultdict
from subprocess import Popen, PIPE, DEVNULL

PROGRAM_DIR = os.getcwd()
SCRIPTS_PATH = PROGRAM_DIR + '/scripts'

class KernelCompiler:
    kernels = defaultdict(list)

    def __init__(self, args):
        for element in args.kernel:
            for kernel in element:
                if os.path.exists(kernel):
                    self.kernels[kernel] = []

    def start(self):
        for kernel in self.kernels.keys():
            print(f"Compiling {kernel}...")

            # @TODO: Write a reliable function to obtain what needs to be compiled and track it with a progress bar.

            os.chdir(kernel)

            # Start the compile and track output.
            with Popen(['make', '-j4'], stdout=PIPE, universal_newlines=True) as compile:
                for line in compile.stdout:
                        # Cut out the file path and extension from the file name.
                        fileParts = line.split()
                        for part in fileParts:
                            if part.endswith(".o"):
                                file_name = os.path.basename(part)[:-2]

                                # Currently used for debugging what is being outputted from the Make process.
                                print(line)
            compile.wait()

            # Install Kernel Modules
            print("Installing built kernel modules...")
            Popen(['make', 'modules_install'], stdout=DEVNULL).wait()

            # Install the Kernel
            print("Installing Kernel into /boot...")
            Popen(['make', 'install'], stdout=DEVNULL).wait()


            # @TODO: Initialize ram fs to allow for booting into the new kernel.


