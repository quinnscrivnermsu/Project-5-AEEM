import os
import argparse
import time
import pandas as pd
from experiment_manager import ExperimentManager, drive, folder_id
from visualization import generate_all_visualizations

DIR_PATH, _ = os.path.split(os.path.abspath(__file__))

parser = argparse.ArgumentParser()
parser.add_argument('-k', '--kerneltorun', action='append', nargs='+')
args = parser.parse_args()

print("Welcome to the Automated Experiment Execution Manager:\n")

manager = ExperimentManager()

if args.kerneltorun is None:
    while True:
        try:
            kernel_num = int(input("Input How Many Kernels Will Be Used: "))
            break
        except ValueError:
            print("Invalid input. Please try again.")
    
    kernel_info = []
    for number in range(kernel_num):
        while True:
            kernel_loc = input(f"Input Kernel {number + 1} Path: ")
            if os.path.exists(kernel_loc):
                kernel_loc = kernel_loc.replace('/boot/', '')
                kernel_info.append(kernel_loc)
                break
            else:
                print("Path does not exist. Please try again.")
    
    exp_data = []
    # For each kernel, ask how many experiments and which benchmarks.
    for kernel in kernel_info:
        new_exp = {"kernel": kernel, "experiments": []}
        exp_num = int(input(f"How many experiments for Kernel ({kernel})?: "))
        for i in range(exp_num):
            benchmark_name = input(f"Enter the benchmark for position {i + 1}: ")
            new_exp["experiments"].append(benchmark_name)
        exp_data.append(new_exp)
    
    manager.load_experiment_data(exp_data)
    manager.write_benchmarks_to_file()
    # Run benchmarks for the first kernel; this will generate the CSV.
    manager.run_benchmarks(exp_data[0]["kernel"])
else:
    manager.run_benchmarks(args.kerneltorun[0][0])

# Wait a few seconds to ensure the CSV file has been written.
time.sleep(3)

csv_file = os.path.join(DIR_PATH, "all_experiment_results.csv")
output_folder = os.path.join(DIR_PATH, "experiment_results")
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

if os.path.exists(csv_file):
    print(f"Found CSV results at: {csv_file}")
    df_all = pd.read_csv(csv_file)
    print("DataFrame loaded, now generating visualizations...")
    generate_all_visualizations(df_all, output_folder)
    print("Visualizations generated successfully.")
else:
    print("CSV results file not found. Please check that experiments ran correctly.")

# Upload the visualization images to Google Drive.
visualizations = ["all_experiments.png", "heatmap_all.png", "bar_chart.png"]
for vis in visualizations:
    vis_path = os.path.join(output_folder, vis)
    if os.path.exists(vis_path):
        try:
            fileUpload = drive.CreateFile({'parents': [{'id': folder_id}]})
            fileUpload.SetContentFile(vis_path)
            fileUpload["title"] = vis
            fileUpload.Upload()
            print(f"Uploaded visualization {vis} to Google Drive.")
        except Exception as e:
            print(f"Error uploading {vis}: {e}")
    else:
        print(f"Visualization file {vis_path} not found!")
