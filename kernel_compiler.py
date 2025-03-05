import os, stat, fileinput, re, distro
from collections import defaultdict
from subprocess import Popen, PIPE, DEVNULL
from pathlib import Path

PROGRAM_DIR = os.getcwd()
SCRIPTS_PATH = PROGRAM_DIR + '/scripts'
DISTRO_NAME = distro.id()
DISTRO_VERSION = distro.version()
CONFIG_FILE = Path(f"/lib/modules/{os.uname().release}/build/.config")

class KernelCompiler:
    kernels = defaultdict(list)

    def __init__(self, args):
        for element in args.kernel:
            for kernel in element:
                if os.path.exists(kernel):
                    self.kernels[kernel] = []

    def setup_environment(self, kernel):
        print(f"Setting up environment for Kernel compilation...")

        # Clean the build directory and create the default config
        Popen(['make', 'mrproper'], stdout=DEVNULL).wait()

        # @TODO: Figure out what were going to do if we don't have a config file here.
        # Use the currently running Kernel config as a base
        Popen("cp /boot/config-$(uname -r) .config", stdout=DEVNULL, shell=True).wait()

        # Update the config to match the Kernel we intend to build with
        Popen(['make', 'olddefconfig'], stdout=DEVNULL, stderr=DEVNULL).wait()

        # This is required as it will fail to compile with Make and exit with Error Code 2 due to the CONFIG_SYSTEM_TRUSTED_KEY
        if DISTRO_NAME == "centos" and DISTRO_VERSION == "9":
            for line in fileinput.input(".config", inplace=True):
                trusted_key_line = re.sub(r'CONFIG_SYSTEM_TRUSTED_KEYS=.*', 'CONFIG_SYSTEM_TRUSTED_KEYS=""', line)
                print(trusted_key_line, end='')


    def start(self, threads):
        print(f"{len(self.kernels.keys())} experiments to compile:\n")

        for kernel in self.kernels.keys():
            KERNEL_NAME = kernel.split('/')[-1]

            print(f"Experiment {KERNEL_NAME}:")
            os.chdir(kernel)

            self.setup_environment(kernel)

            # Start the compile and track output.
            print("Starting compile...")

            # @TODO: In the future, we can use compile for error handing and logging.
            Popen(['make', f'-j{threads}'], stdout=DEVNULL, universal_newlines=True).wait()

            print("Compile successful!")

            # Install Kernel Modules
            print("Installing built kernel modules...")
            Popen(['make', 'modules_install'], stdout=DEVNULL).wait()

            # Install the Kernel
            print(f"Installing {KERNEL_NAME} into /boot...")
            Popen(['make', 'install'], stdout=DEVNULL).wait()
            print("\n")

            # @TODO: Initialize ram fs to allow for booting into the new kernel.