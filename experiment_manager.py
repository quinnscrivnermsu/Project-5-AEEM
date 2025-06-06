import os, time, re
from subprocess import PIPE, DEVNULL, Popen
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from crontab import CronTab
import pandas as pd
import smtplib
from email.message import EmailMessage
from visualization import generate_all_visualizations

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DIR_PATH, FILE_PATH = os.path.split(os.path.abspath(__file__))
GAPBS_PATH = DIR_PATH + '/gapbs/'
CRON = CronTab(user=True)

# Authenticate with Google Drive.
gauth = GoogleAuth()
gauth.LoadCredentialsFile("aeem_creds.txt")
if gauth.credentials is None:
    gauth.GetFlow()
    gauth.flow.params.update({'access_type': 'offline'})
    gauth.flow.params.update({'approval_prompt': 'force'})
    gauth.LocalWebserverAuth()

elif gauth.access_token_expired:
    gauth.Refresh()
else:
    gauth.Authorize()

gauth.SaveCredentialsFile("aeem_creds.txt")

drive = GoogleDrive(gauth)

#Specify the Folder ID that gets the uploaded files. 
folder_id = '1ejmiLZweyhIZtv_Fi_3KzsMmMYNjPjEa'

# 2FA accounts will need to generate app password. Generate from Google Account > Security > App Passwords
sender_email = "aeemproject@gmail.com"
# This is the app password for the google 2fa, will need to be changed if the sender email gets changed. 
sender_password = os.getenv("SENDER_PASSWORD")
to_email = "aeemproject@gmail.com"

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
                        file.write(f"{command}\n")

    def log_event(self, event, level = "INFO"):
        event_log = f"{time.ctime()}: [{level}] {event}"

        with open(os.path.join(DIR_PATH, 'log.txt'), "a") as log_file:
            log_file.write(event_log + "\n")
        
        print(event_log)

    def get_next_kernel(self, current_kernel):
        try:
            benchmark_files = sorted([file for file in os.listdir(DIR_PATH) if file.endswith('.txt') ])
            
            current_file = benchmark_files.index(current_kernel + '.txt')
            if current_file >= len(benchmark_files) - 1:
                return None
            
            return benchmark_files[current_file + 1].replace('.txt', '')
        except ValueError:
            return None # Doesn't exist or not found in the file list

    # Email sending function.
    def send_email(self, subject, body, to_email, attachment_paths=None, sender_email=sender_email, sender_password=sender_password):
        msg = EmailMessage()
        
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = to_email
        msg.set_content(body)
        
        # Attach each file to the email
        if attachment_paths:
            for attachment_path in attachment_paths:
                if os.path.exists(attachment_path):
                    with open(attachment_path, 'rb') as f:
                        file_data = f.read()
                    msg.add_attachment(
                        file_data,
                        maintype='application',
                        subtype='octet-stream',
                        filename=os.path.basename(attachment_path)
                    )
        
        try:
            # Using Google SMTP
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender_email, sender_password)
                server.send_message(msg)
            self.log_event("Experiment email sent successfully.")
        except Exception as e:
            self.log_event(f"Failed to send email: {e}", "ERROR")

    def setup_environment(self, kernel):
        self.log_event(f"Setting up environment...")

        # Write to the systems crontab
        job_command = f"python {DIR_PATH}/run.py --kerneltorun { kernel }"
        job = CRON.new(command=job_command, comment=f'AEEM-Kernel({kernel})')
        job.every_reboot()
        CRON.write()

        # Switch the kernel and reboot.
        self.log_event("System will reboot in 10 seconds and start the experiment!")
        Popen(['grubby', '--set-default', '/boot/' + kernel], stdout=DEVNULL, stderr=DEVNULL).wait()
        time.sleep(10)
        Popen(['shutdown', '-r', 'now'])


    def run_benchmarks(self, current_kernel):
        self.log_event(f"Starting Experiments for Kernel {current_kernel}...")

        # Get current kernel cron entry and remove it
        CRON.remove_all(comment=f'AEEM-Kernel({current_kernel})')
        CRON.write()

        # Retrieve the next kernel to be ran
        next_kernel = self.get_next_kernel(current_kernel)
        
        benchmark_file = current_kernel + '.txt'
        if not os.path.exists(os.path.join(DIR_PATH, benchmark_file)):
            self.log_event("No benchmarks found for this kernel. Exiting...", "WARN")

            if next_kernel is None:
                exit() # Exit the program as we don't have any more benchmarks to run.
            else:
                self.setup_environment(next_kernel) # Switch to the next kernel
                return

        all_results = []

        # Open our text file and run all of our benchmarks
        with open(os.path.join(DIR_PATH, benchmark_file)) as file:
            for command in file:
                clean_command = command.strip()

                full_command = clean_command
                experiment = Popen(full_command, stdout=PIPE, stderr=PIPE, shell=True)
                output, error = experiment.communicate()

                experiment_results = output.decode('utf-8', errors='ignore')
                error_results = error.decode('utf-8', errors='ignore')

                # Extract -g input size from the command
                size_match = re.search(r"-g\s+(\d+)", full_command)
                input_size = int(size_match.group(1)) if size_match else -1

                results_file = "results.txt"
                error_file = "errResults.txt"

                with open(os.path.join(DIR_PATH, results_file), "a") as f:
                    f.write(f"Experiment {clean_command} (Kernel {current_kernel}):\n")
                    f.write(experiment_results)
                    f.write('\n\n')

                with open(os.path.join(DIR_PATH, error_file), "a") as f:
                    f.write(f"Experiment {clean_command} (Kernel {current_kernel}):\n")
                    f.write(error_results)
                    f.write('\n\n')

                if error_results:
                    self.log_event(f"Error in command {clean_command}", "ERROR")
                    self.send_email(
                        subject=f"Experiment {full_command} failed",
                        body=f"Command {full_command} failed. Details of the error can be found in the attached file.",
                        to_email=to_email,
                        attachment_paths=[error_file],
                    )
                    continue

                time_match = re.search(r"Average Time:\s*([0-9.]+)", experiment_results)
                exec_time = float(time_match.group(1)) if time_match else -1
            
                all_results.append({
                        "Kernel": current_kernel,
                        "Benchmark": clean_command,
                        "Input Size": input_size,
                        "Execution Time": exec_time,
                        "Test": clean_command
                    })

                # Notify the user of the completion of the experiment
                self.send_email(
                    subject=f"Experiment {full_command} completed",
                    body=f"Command {full_command} completed. Results have been saved.",
                    to_email=to_email,
                    attachment_paths=[results_file, error_file],
                )

                self.log_event(f"Command {full_command} completed. Results saved.")

        # Save CSV
        df_results = pd.DataFrame(all_results)
        csv_path = os.path.join(DIR_PATH, "all_experiment_results.csv")
        df_results.to_csv(csv_path, index=False)
        self.log_event(f"Results saved to {csv_path}")

        # Upload CSV
        fileUpload = drive.CreateFile({'parents': [{'id': folder_id}]})
        fileUpload.SetContentFile(csv_path)
        fileUpload["title"] = "all_experiment_results.csv"
        fileUpload.Upload()
        self.log_event(f"Uploaded CSV to Google Drive.")

        # Generate and upload visualizations
        output_folder = os.path.join(DIR_PATH, "experiment_results")
        os.makedirs(output_folder, exist_ok=True)
        generate_all_visualizations(df_results, output_folder)
        self.log_event("All visualizations generated successfully.")

        for vis_file in ["all_experiments.png", "heatmap_all.png"]:
            vis_path = os.path.join(output_folder, vis_file)
            if os.path.exists(vis_path):
                vis_upload = drive.CreateFile({'parents': [{'id': folder_id}], 'title': vis_file})
                vis_upload.SetContentFile(vis_path)
                vis_upload.Upload()
                self.log_event(f"Uploaded {vis_file} to Google Drive.")
        
        if next_kernel is not None:
            self.setup_environment(next_kernel)
        else:
            self.log_event("All experiments have completed!")
            self.send_email(
                subject="AEEM experiments data",
                body="All of the running experiments have completed and the results have been attached to this email.",
                to_email=to_email,
                attachment_paths=[results_file, csv_path, vis_path]
            )

            # Clean up experiment files 
            os.remove(os.path.join(DIR_PATH, results_file))
            os.remove(os.path.join(DIR_PATH, error_file))
            os.remove(os.path.join(DIR_PATH, csv_path))
            os.remove(os.path.join(DIR_PATH, vis_path))

            exit()
            
    def start(self):
        first_kernel = next(iter(self.kernels))
        self.setup_environment(first_kernel)
