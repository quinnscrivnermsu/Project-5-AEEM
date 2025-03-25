import os, stat, fileinput, re, time
from subprocess import PIPE, DEVNULL, Popen
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from crontab import CronTab

DIR_PATH, FILE_PATH = os.path.split(os.path.abspath(__file__))
GAPBS_PATH = DIR_PATH + '/gapbs/'
CRON = CronTab(user=True)

# Authenticate and Create PyDrive Client
# gauth = GoogleAuth()
# gauth.LocalWebserverAuth()
# drive = GoogleDrive(gauth)

#Specify the Folder ID that gets the uploaded files. 
folder_id = '1ejmiLZweyhIZtv_Fi_3KzsMmMYNjPjEa'

class ExperimentManager:
    kernels = []
    exps = []

    def __init__(self, exp_data):
        for data in exp_data:
            exp_kernel = data['kernel']
            if os.path.exists(exp_kernel):
                self.kernels.append(exp_kernel)

            self.exps.append(data['experiments'])

    def setup_environment(self):
        print(f"Setting up environment...")

        try:
            next_kernel = self.current_kernel + 1
            
            # Add a new cron job entry to run the next experiment
            job_command = f"python {DIR_PATH}/run.py --experiment { next_kernel }"
            for kernel in self.kernels:
                job_command += f' --kernel {kernel}'
            
            job = CRON.new(command=job_command, comment=f'AEEM-Kernel{next_kernel}')
            job.every_reboot()
            CRON.write()

            # Switch the kernel and reboot.
            print("System will reboot in 10 seconds and start the experiment!")
            Popen(['grubby', '--set-default', self.kernels[ next_kernel ]], stdout=DEVNULL, stderr=DEVNULL).wait()
            time.sleep(10)
            Popen(['shutdown', '-r', 'now'])

        except IndexError:
            print("Kernel does not exist!")
            exit()


    def run_benchmark(self, test, run_next):
        print("Starting Experiment...\n")

        # @TODO: Loop through all of the GAPBS benchmarks specified and wait for each one to finish.

        # An example test is: bfs -g 10 -n 1 (This implies the user has installed all of the benchmarks to /usr/bin/)
        Popen([GAPBS_PATH + test, '-g', '10', '-n', '1']).wait()
        

        # upload the files to Google Drive 
        # TODO Miah, figure out how we will store results and change the line with "SetContentFile" to the experiment results.
        # fileUpload = drive.CreateFile({'parents': [{'id': folder_id}]})
        # fileUpload.SetContentFile('HousePrice.csv')
        # fileUpload.Upload()

        print("Experiment complete!")

        if run_next:
            self.setup_environment()
        else:
            print("All experiments complete!")
            exit()


    def start(self, kernel):
        self.current_kernel = kernel

        # If the current kernel is -1 then we assume we are starting from the very first kernel
        if self.current_kernel == -1:
            self.setup_environment()
        else:
            # Get the last cron entry and remove it.
            CRON.remove_all(comment=f'AEEM-Kernel{self.current_kernel}')

            next_kernel = self.current_kernel + 1
            if next_kernel >= 0 and next_kernel < len(self.kernels):
                self.run_benchmark('bfs', True)
            else:
                self.run_benchmark('bfs', False)