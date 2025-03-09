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

        if args.experiment is not None:
            self.current_exp = int(args.experiment)
            
            if self.current_exp >= len(self.exps):
                print("Invalid experiment number provided")
                exit()
        else: 
            print(f"{len(self.exps)} experiments to run:\n")
            self.current_exp = 0

    def setup_environment(self, experiment):
        print(f"Setting up environment...")

    def run_benchmark(self, test):
        print("Starting Experiment...\n")
        
        # An example test is: bfs -g 10 -n 1
        Popen([GAPBS_PATH + test, '-g', '10', '-n', '1']).wait()

        # Figure out a way to switch the kernel and then run the next experiment.
        
        print("Experiment complete!")
        

        # @TODO Quinn: Store it in the cloud server, after visualization
        # upload the files to Google Drive 
        # fileUpload = drive.CreateFile({'parents': [{'id': folder_id}]})
        # fileUpload.SetContentFile("RESULTDATA.CSV")
        # fileUpload.Upload()


    def start(self):
        experiment = self.exps[ self.current_exp ]

        print(f"Running Experiment {experiment}:\n")

        self.setup_environment(experiment)
        self.run_benchmark('bfs')