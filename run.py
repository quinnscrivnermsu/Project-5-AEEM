import os
import argparse
import time
import pandas as pd
import smtplib
from email.message import EmailMessage
import getpass
from experiment_manager import ExperimentManager, drive, folder_id
from visualization import generate_all_visualizations

# Email sending function.
def send_email(subject, body, to_email, attachment_path=None, sender_email=None, sender_password=None):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = to_email
    msg.set_content(body)
    
    # Attach a file if provided.
    if attachment_path and os.path.exists(attachment_path):
        with open(attachment_path, 'rb') as f:
            file_data = f.read()
        msg.add_attachment(
            file_data,
            maintype='application',
            subtype='octet-stream',
            filename=os.path.basename(attachment_path)
        )
    
    try:
        # Using Office365 SMTP
        with smtplib.SMTP("smtp.office365.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Get the directory where run.py is located.
DIR_PATH, _ = os.path.split(os.path.abspath(__file__))

# Prompt for email credentials at the beginning
print("Please provide your email credentials for notifications:")
sender_email = input("Enter your university email address (e.g., your_email@missouristate.edu): ").strip()
sender_password = getpass.getpass("Enter your email password (or app password): ")

parser = argparse.ArgumentParser()
parser.add_argument('-k', '--kerneltorun', action='append', nargs='+')
args = parser.parse_args()

print("Welcome to the Automated Experiment Execution Manager:\n")

manager = ExperimentManager()

if args.kerneltorun is None:
    # Interactive mode: ask user for kernel details.
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

# Send email notification upon successful completion.
recipient_email = "recipient@missouristate.edu"  # Change to the actual recipient address.
subject = "Experiments Completed Successfully"
body = ("The experiments have finished executing, and the CSV results along with visualizations have been "
        "generated and uploaded to Google Drive.")
attachment = csv_file  # Optionally attach the CSV file.

send_email(subject, body, recipient_email, attachment_path=attachment, sender_email=sender_email, sender_password=sender_password)
