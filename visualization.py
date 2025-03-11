import os
import matplotlib.pyplot as plt
import seaborn as sns

#Generates a line plot comparing execution time across all experiments.
def generate_line_plot(df_all, output_folder):
    plt.figure(figsize=(8, 5))
    #Filters the data and plots a line showing how the execution time changes with the input size
    for exp_name in df_all["Test"].unique():
        exp_data = df_all[df_all["Test"] == exp_name]
        plt.plot(exp_data["Input Size"], exp_data["Execution Time"],
                 marker='o', linestyle='-', label=exp_name)
    plt.xlabel("Input Size")
    plt.ylabel("Execution Time (seconds)")
    plt.title("Final Execution Time Comparison Across All Experiments")
    plt.legend()
    plt.grid(True)
    #Saves plot as all_experiments.png in output folder
    file_all_exp = os.path.join(output_folder, "all_experiments.png")
    plt.savefig(file_all_exp)
    plt.close()
    print(f"Line plot saved to: {file_all_exp}")

#Generates a heatmap comparing execution times across experiments.
def generate_heatmap(df_all, output_folder):
    plt.figure(figsize=(8, 5))
    # Pivot the DataFrame for the heatmap
    heatmap_data = df_all.pivot(index="Input Size", columns="Test", values="Execution Time")
    sns.heatmap(heatmap_data, annot=True, cmap='coolwarm', fmt=".2f")
    plt.title("Execution Time Heatmap Across All Experiments")
    plt.xlabel("Experiments")
    plt.ylabel("Input Size")
    #Heatmap saved as heatmap_all.png
    file_heatmap = os.path.join(output_folder, "heatmap_all.png")
    plt.savefig(file_heatmap)
    plt.close()
    print(f"Heatmap saved to: {file_heatmap}")

#Generates all visualizations: line plot and heatmap.
def generate_all_visualizations(df_all, output_folder):
    generate_line_plot(df_all, output_folder)
    generate_heatmap(df_all, output_folder)
    print("All visualizations generated successfully.")
