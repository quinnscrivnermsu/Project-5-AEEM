# Project-5-AEEM
Automated Experiment Execution Manager created by Dre Woolston, Mark Thompson, Miah Weems, and Quinn Scrivner

# How to Start Experiments
**FIRST** `python run.py`

The user will then be prompted to input the number of kernels that experiments will be run on. 

Next, the user will be prompted to enter the file paths for each kernel.

Then, the user will be prompted for the number of experiments to run on each kernel.

Lastly, the user will be prompted to enter the shell command to use for each experiment (Ex. `/home/gapbs/bfs -g 10 -n 1`)

The program will then start a timer and then reboot and begin the experiments.

After each experiment:
- The results will be saved
- Visual graphs will be generated
- Files will be uploaded to Google Drive
- An email notification will be sent

# How to Setup PyDrive & Obtain client_secrets.json
https://pythonhosted.org/PyDrive/quickstart.html

# How to Run Experiments Without Switching Kernels
1. Create a text file in the project directory
2. Run the python program with the following arguments `python run.py --kerneltorun <textFileName>.txt
3. Observe the results in the log files

# How to Enable Email Notifications
This project uses **email notifications** to alert users when experiments complete.

Because most email accounts have **two-factor authentication (2FA)**, you must set up an **App Password**.

Steps:
1. Go to your [Google Account Security Settings](https://myaccount.google.com/security)
2. Under "Signing in to Google," select **App Passwords**
3. Create a new App Password (you can name it "AEEM Script")
4. Copy the 16-character generated password
5. Create a `.env` file in the project directory containing: SENDER_PASSWORD=your_generated_app_password_here

# Dependencies
- pydrive
- python-crontab
- pandas
- matplotlib
- seaborn
- dotenv

# Features Summary
- Fully automated experiment execution
- Kernel switching (only on Linux systems)
- Logging of results and errors
- Visual graph generation
- Automatic upload to Google Drive
- Email notifications with attachments

