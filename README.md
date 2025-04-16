# Project-5-AEEM
Automated Experiment Execution Manager created by Dre Woolston, Mark Thompson, Miah Weems, and Quinn Scrivner

# How to Start Experiments
**FIRST** `python run.py`

The user will then be prompted to input the number of kernels that experiments will be run on. 

Next, the user will be prompted to enter the file paths for each kernel.

Then, the user will be prompted for the number of experiments to run on each kernel.

Lastly, the user will be prompted to enter the shell command to use for each experiment (Ex. `/home/gapbs/bfs -g 10 -n 1`)

The program will then start a timer and then reboot and begin the experiments.

# How to Setup PyDrive & Obtain client_secrets.json
https://pythonhosted.org/PyDrive/quickstart.html

# How to Run Experiments Without Switching Kernels
1. Create a text file in the project directory
2. Run the python program with the following arguments `python run.py --kerneltorun <textFileName>.txt
3. Observe the results in the log files

# Dependencies
- pydrive
- python-crontab

