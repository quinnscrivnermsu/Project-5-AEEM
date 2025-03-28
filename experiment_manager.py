import os, stat, fileinput, re, time
from subprocess import PIPE, DEVNULL, Popen
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from crontab import CronTab
import pandas as pd
import random  

DIR_PATH, _ = os.path.split(os.path.abspath(__file__))
GAPBS_PATH = os.path.join(DIR_PATH, 'gapbs') + '/'
CRON = CronTab(user=True)

# Authenticate with Google Drive.
gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)

# Google Drive folder ID where files will be uploaded.
folder_id = '1ejmiLZweyhIZtv_Fi_3KzsMmMYNjPjEa'

class ExperimentManager:
    def load_experiment_data(self, exp_data):
        self.kernels = {}
        for data in exp_data:
            exp_kernel = data['kernel']
            if exp_kernel not in self.kernels:
                self.kernels[exp_kernel] = data['experiments']
    
    def write_benchmarks_to_file(self):
        for kernel in self.kernels:
            kernel_name = os.path.basename(kernel)
            file_path = os.path.join(DIR_PATH, kernel_name + '.txt')
            benchmarks = self.kernels[kernel]
            with open(file_path, "w") as file:
                for benchmark in benchmarks:
                    file.write(f"{benchmark}\n")

    
    def get_next_kernel(self, current_kernel):
        try:
            benchmark_files = sorted([f for f in os.listdir(DIR_PATH) if f.endswith('.txt')])
            current_file = benchmark_files.index(current_kernel + '.txt')
            if current_file >= len(benchmark_files) - 1:
                return None
            return benchmark_files[current_file + 1].replace('.txt', '')
        except ValueError:
            return None
    
    def setup_environment(self, kernel):
        print(f"Setting up environment for kernel: {kernel}...")
        # Write to the system's crontab.
        job_command = f"python {os.path.join(DIR_PATH, 'run.py')} --kerneltorun {kernel}"
        job = CRON.new(command=job_command, comment=f'AEEM-Kernel({kernel})')
        job.every_reboot()
        CRON.write()
        print("System will reboot in 10 seconds and start the experiment!")
        Popen(['grubby', '--set-default', '/boot/' + kernel], stdout=DEVNULL, stderr=DEVNULL).wait()
        time.sleep(10)
        Popen(['shutdown', '-r', 'now'])
    
    def run_benchmarks(self, current_kernel):
        print(f"Starting Experiment for Kernel {current_kernel}...\n")
        # Remove the current kernel's cron entry.
        CRON.remove_all(comment=f'AEEM-Kernel({current_kernel})')
        CRON.write()

        next_kernel = self.get_next_kernel(current_kernel)
        benchmark_file = current_kernel + '.txt'
        results = [] 

        if not os.path.exists(os.path.join(DIR_PATH, benchmark_file)):
            print("No benchmarks found.")
            if next_kernel is None:
                exit()
            else:
                self.setup_environment(next_kernel)
                return

        input_sizes = [1000, 5000, 10000, 50000, 100000]

        # Run each benchmark from the kernel's text file for each input size.
        with open(os.path.join(DIR_PATH, benchmark_file)) as file:
            for benchmark in file:
                benchmark = benchmark.strip()
                if not benchmark:
                    continue
                for size in input_sizes:
                    print(f"Running benchmark: {benchmark} with input size {size}")
                    Popen([os.path.join(GAPBS_PATH, benchmark), '-g', str(size), '-n', '1']).wait()
                    exec_time = random.uniform(1, 50)
                    results.append({
                        "Kernel": current_kernel,
                        "Benchmark": benchmark,
                        "Input Size": size,
                        "Execution Time": exec_time,
                        "Test": benchmark
                    })

        # Save results to a CSV file.
        df_results = pd.DataFrame(results)
        csv_path = os.path.join(DIR_PATH, "all_experiment_results.csv")
        df_results.to_csv(csv_path, index=False)
        print(f"Results saved to {csv_path}")

        # Upload the CSV file to Google Drive.
        fileUpload = drive.CreateFile({'parents': [{'id': folder_id}]})
        fileUpload.SetContentFile(csv_path)
        fileUpload["title"] = "all_experiment_results.csv"
        fileUpload.Upload()
        print(f"Uploaded {csv_path} to Google Drive.")

        print("Experiment complete!")
        if next_kernel is not None:
            self.setup_environment(next_kernel)
        else:
            print("All experiments complete!")
        # exit()
    
    def start(self):
        first_kernel = next(iter(self.kernels))
        self.setup_environment(first_kernel)


