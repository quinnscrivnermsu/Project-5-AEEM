import os, time
from subprocess import PIPE, DEVNULL, Popen
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from crontab import CronTab

DIR_PATH, FILE_PATH = os.path.split(os.path.abspath(__file__))
GAPBS_PATH = DIR_PATH + '/gapbs/'
CRON = CronTab(user=True)

# Authenticate and Create PyDrive Client
#gauth = GoogleAuth()
#gauth.LocalWebserverAuth()
#drive = GoogleDrive(gauth)

#Specify the Folder ID that gets the uploaded files. 
#folder_id = '1ejmiLZweyhIZtv_Fi_3KzsMmMYNjPjEa'

class ExperimentManager:
    def load_experiment_data(self, exp_data):
        self.kernels = {}
        
        for data in exp_data:
            exp_kernel = data['kernel']
            if exp_kernel not in self.kernels:
                self.kernels[exp_kernel] = data['experiments']
    
    def write_benchmarks_to_file(self):
        for kernel in self.kernels:
            commands = self.kernels[kernel]

            with open(os.path.join(DIR_PATH, kernel + '.txt'), "w") as file:
                    for command in commands:
                        file.write(f"{command}")

    def get_next_kernel(self, current_kernel):
        try:
            benchmark_files = sorted([file for file in os.listdir(DIR_PATH) if file.endswith('.txt') ])
            
            current_file = benchmark_files.index(current_kernel + '.txt')
            if current_file >= len(benchmark_files) - 1:
                return None
            
            return benchmark_files[current_file + 1].replace('.txt', '')
        except ValueError:
            return None # Doesn't exist or not found in the file list

    def setup_environment(self, kernel):
        print(f"Setting up environment...")

        # Write to the systems crontab
        job_command = f"python {DIR_PATH}/run.py --kerneltorun { kernel }"
        job = CRON.new(command=job_command, comment=f'AEEM-Kernel({kernel})')
        job.every_reboot()
        CRON.write()

        # Switch the kernel and reboot.
        print("System will reboot in 10 seconds and start the experiment!")
        Popen(['grubby', '--set-default', '/boot/' + kernel], stdout=DEVNULL, stderr=DEVNULL).wait()
        time.sleep(10)
        Popen(['shutdown', '-r', 'now'])


    def run_benchmarks(self, current_kernel):
        print(f"Starting Experiment for Kernel {current_kernel}...\n")

        # Get current kernel cron entry and remove it
        CRON.remove_all(comment=f'AEEM-Kernel({current_kernel})')
        CRON.write()

        # Retrieve the next kernel to be ran
        next_kernel = self.get_next_kernel(current_kernel)
        
        benchmark_file = current_kernel + '.txt'
        if not os.path.exists(os.path.join(DIR_PATH, benchmark_file)):
            print("No benchmarks found.")

            if next_kernel is None:
                exit() # Exit the program as we don't have any more benchmarks to run.
            else:
                self.setup_environment(next_kernel) # Switch to the next kernel
                return

        # Open our text file and run all of our benchmarks
        with open(os.path.join(DIR_PATH, benchmark_file)) as file:
            for command in file:
                experiment = Popen(command, stdout=PIPE, stderr=PIPE, shell=True)

                # Retrieve output and errors from the command that was ran. (This will wait for the experiment to finish before returning the output and error)
                output, error = experiment.communicate()

                # Upload the complete experiment file to the Google Drive
                # TODO Quinn Send output, both error and not error, to the SSS
                experiement_results = output
                error_results = error

                results_file = "results.txt"
                error_file = "errResults.txt"

                with open(os.path.join(DIR_PATH, results_file), "w") as f:
                    f.write(experiement_results)

                # r_file = drive.CreateFile({'parents': [{'id': folder_id}], 'title': results_file})
                # r_file.Upload()

                with open(os.path.join(DIR_PATH, error_file), "w") as f:
                    f.write(error_results)

                # r_file = drive.CreateFile({'parents': [{'id': folder_id}], 'title': error_file})
                # r_file.Upload()


        print("Experiment complete!")

        if next_kernel is not None:
            self.setup_environment(next_kernel)
        else:
            print("All experiments complete!")
            exit()
            
    def start(self):
        first_kernel = next(iter(self.kernels))
        self.setup_environment(first_kernel)
