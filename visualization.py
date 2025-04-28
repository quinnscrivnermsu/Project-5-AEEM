import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np 

# Generates a line plot comparing execution time across all experiments.
def generate_line_plot(df_all, output_folder):
    plt.figure(figsize=(8, 5))
    for exp_name in df_all["Test"].unique():
        exp_data = df_all[df_all["Test"] == exp_name]
        plt.plot(exp_data["Input Size"], exp_data["Execution Time"],
                 marker='o', linestyle='-', label=exp_name)
    plt.xlabel("Input Size")
    plt.ylabel("Execution Time (seconds)")
    plt.title("Final Execution Time Comparison Across All Experiments")
    plt.legend()
    plt.grid(True)
    file_all_exp = os.path.join(output_folder, "all_experiments.png")
    plt.savefig(file_all_exp)
    plt.close()

    #print(f"Line plot saved to: {file_all_exp}")

# Generates a heatmap comparing execution times across experiments.
def generate_heatmap(df_all, output_folder):
    plt.figure(figsize=(8, 5))
    heatmap_data = df_all.pivot_table(index="Input Size", columns="Test", values="Execution Time", aggfunc="mean")
    sns.heatmap(heatmap_data, annot=True, cmap='coolwarm', fmt=".2f")
    plt.title("Execution Time Heatmap Across All Experiments")
    plt.xlabel("Experiments")
    plt.ylabel("Input Size")
    file_heatmap = os.path.join(output_folder, "heatmap_all.png")
    plt.savefig(file_heatmap)
    plt.close()

    #print(f"Heatmap saved to: {file_heatmap}")

# Generates a bar chart showing average execution time per benchmark.
def generate_bar_chart(df_all, output_folder):
    plt.figure(figsize=(8, 5))
    avg_times = df_all.groupby("Test")["Execution Time"].mean().reset_index()
    sns.barplot(x="Test", y="Execution Time", data=avg_times)
    plt.title("Average Execution Time per Experiment")
    plt.xlabel("Experiment")
    plt.ylabel("Average Execution Time (seconds)")
    file_bar_chart = os.path.join(output_folder, "bar_chart.png")
    plt.savefig(file_bar_chart)
    plt.close()

    #print(f"Bar chart saved to: {file_bar_chart}")

# Generates all visualizations: line plot, heatmap, and bar chart.
def generate_all_visualizations(df_all, output_folder):
    generate_line_plot(df_all, output_folder)
    generate_heatmap(df_all, output_folder)
    generate_bar_chart(df_all, output_folder)
