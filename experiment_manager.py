import os, stat, fileinput, re
from subprocess import PIPE, DEVNULL, Popen
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from crontab import CronTab

PROGRAM_DIR = os.getcwd()
GAPBS_PATH = PROGRAM_DIR + '/gapbs/'
SCRIPTS_PATH = PROGRAM_DIR + '/scripts'
CRON = CronTab(user=True)

# Authenticate and Create PyDrive Client
# gauth = GoogleAuth()
# gauth.LocalWebserverAuth()
# drive = GoogleDrive(gauth)

#Specify the Folder ID that gets the uploaded files. 
folder_id = '1ejmiLZweyhIZtv_Fi_3KzsMmMYNjPjEa'

class ExperimentManager:
    exps = []

    def __init__(self, args):
        for element in args.kernel:
            for experiment in element:
                if os.path.exists(experiment):
                    self.exps.append(experiment)

    def setup_environment(self, queue_next):
        print(f"Setting up environment...")

        # Get the last cron entry and remove it.
        CRON.remove_all(comment=f'AEEM-Experiment{self.current_exp}')

        if queue_next:
            next_exp = self.current_exp + 1

            # Add a new cron job entry to run the next experiment
            job_command = f"python {PROGRAM_DIR}/run.py --experiment { next_exp }"
            for kernel in self.exps:
                job_command += f' --kernel {kernel}'

            
            job = CRON.new(command=job_command, comment=f'AEEM-Experiment{next_exp}')
            job.every_reboot()
            CRON.write()

        # Switch the Kernel and Reboot.
        kernel_version = self.exps[ self.current_exp ].split('/boot/vmlinuz-')[-1]

        print("System will now reboot into the new kernel and begin the experiment..")
        Popen(['kexec', '-l', self.exps[ next_exp ], f'--initrd=/boot/initramfs-{kernel_version}.img', '--reuse-cmdline']).wait()
        Popen(['kexec', '-e'])


    def run_benchmark(self, test, run_next):
        print("Starting Experiment...\n")

        # An example test is: bfs -g 10 -n 1
        Popen([GAPBS_PATH + test, '-g', '10', '-n', '1']).wait()

        print("Experiment complete!")
        

        # @TODO Quinn: Store it in the cloud server, after visualization
        # upload the files to Google Drive 
        # fileUpload = drive.CreateFile({'parents': [{'id': folder_id}]})
        # fileUpload.SetContentFile("RESULTDATA.CSV")
        # fileUpload.Upload()

        if run_next:
            self.setup_environment()
        else:
            print("All experiments complete!")
            exit()


    def start(self, exp):
        self.current_exp = exp

        # If the current experiment is -1 then we assume we are starting from the very first experiment
        if self.current_exp == -1:
            self.setup_environment()
        else:
            next_exp = self.current_exp + 1
            if next_exp >= 0 and next_exp < len(self.exps):
                self.run_benchmark('bfs', True)
            else:
                self.run_benchmark('bfs', False)