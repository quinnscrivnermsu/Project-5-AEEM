import os, stat, fileinput, re
from subprocess import PIPE, DEVNULL, Popen
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from crontab import CronTab

# Import visualization functions from the separate file
from visualization import generate_all_visualizations

PROGRAM_DIR = os.getcwd()
GAPBS_PATH = os.path.join(PROGRAM_DIR, 'gapbs')  # Use os.path.join for consistency
SCRIPTS_PATH = os.path.join(PROGRAM_DIR, 'scripts')
CRON = CronTab(user=True)

# Authenticate and Create PyDrive Client
gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)

# Specify the Folder ID that gets the uploaded files.
folder_id = '1ejmiLZweyhIZtv_Fi_3KzsMmMYNjPjEa'

# Ensure the output folder exists
output_folder = os.path.join(PROGRAM_DIR, "experiment_results")
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

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
        print(f"Setting up environment for {experiment}...")

# Runs a GAP benchmark and stores the execution time results.
    def run_benchmark(self, test, input_size):
        print(f"Starting Experiment: {test} with Input Size {input_size}...\n")
        # Run the benchmark (example: bfs -g <input_size> -n 1)
        Popen([os.path.join(GAPBS_PATH, test), '-g', str(input_size), '-n', '1']).wait()
        print("Experiment complete!")
        
        # Simulate storing the result (replace with actual measurement)
        import numpy as np
        import pandas as pd
        execution_time = np.random.uniform(1, 50)  # simulated execution time
        df = pd.DataFrame({'Execution Time': [execution_time]})
        result_file = os.path.join(output_folder, f"{test}_results_{input_size}.csv")
        df.to_csv(result_file, index=False)
        
        # Upload the result file to Google Drive
        fileUpload = drive.CreateFile({'parents': [{'id': folder_id}]})
        fileUpload.SetContentFile(result_file)
        fileUpload.Upload()
        print(f"Uploaded {result_file} to Google Drive.")
        return df

    def start(self):
        experiment = self.exps[self.current_exp]
        print(f"Running Experiment {experiment}:\n")
        self.setup_environment(experiment)
        
        # For demonstration, run benchmark 'bfs' with various input sizes
        import pandas as pd
        input_sizes = [1000, 5000, 10000, 50000, 100000]
        results_list = []
        for size in input_sizes:
            df_result = self.run_benchmark('bfs', size)
            df_result['Input Size'] = size
            df_result['Test'] = 'bfs'
            results_list.append(df_result)
        
        all_results = pd.concat(results_list)
        all_results_file = os.path.join(output_folder, "all_experiment_results.csv")
        all_results.to_csv(all_results_file, index=False)
        print(f"All experiment results saved to {all_results_file}.")
        
        # Generate visualizations using the separate visualization module
        generate_all_visualizations(all_results, output_folder)

if __name__ == "__main__":
    class Args:
        kernel = [["bfs", "pr", "cc"]]  # Example kernels to be tested
        experiment = None
    args = Args()
    manager = ExperimentManager(args)
    manager.start()
