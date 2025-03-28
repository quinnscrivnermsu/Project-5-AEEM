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
    print(f"Line plot saved to: {file_all_exp}")

# Generates a heatmap comparing execution times across experiments.
def generate_heatmap(df_all, output_folder):
    plt.figure(figsize=(8, 5))
    heatmap_data = df_all.pivot(index="Input Size", columns="Test", values="Execution Time")
    sns.heatmap(heatmap_data, annot=True, cmap='coolwarm', fmt=".2f")
    plt.title("Execution Time Heatmap Across All Experiments")
    plt.xlabel("Experiments")
    plt.ylabel("Input Size")

    file_heatmap = os.path.join(output_folder, "heatmap_all.png")
    plt.savefig(file_heatmap)
    plt.close()
    print(f"Heatmap saved to: {file_heatmap}")

# Generates a grouped bar chart comparing execution times across experiments.
def generate_bar_chart(df_all, output_folder):
    pivoted = df_all.pivot(index="Input Size", columns="Test", values="Execution Time")
    input_sizes = pivoted.index
    tests = pivoted.columns
    x = np.arange(len(input_sizes))
    bar_width = 0.2  # Adjust as needed
    plt.figure(figsize=(8, 5))
    # Plot each experiment as a separate set of bars
    for i, test in enumerate(tests):
        plt.bar(
            x + i * bar_width,       
            pivoted[test],          
            bar_width,              
            label=test             
        )
    plt.xlabel("Input Size")
    plt.ylabel("Execution Time (seconds)")
    plt.title("Execution Time Comparison (Bar Chart)")
    plt.xticks(x + bar_width * (len(tests) - 1) / 2, input_sizes)
    plt.legend()
    plt.grid(axis="y")

    bar_chart_path = os.path.join(output_folder, "bar_chart.png")
    plt.savefig(bar_chart_path)
    plt.close()
    print(f"Bar chart saved to: {bar_chart_path}")

# Generates both visualizations.
def generate_all_visualizations(df_all, output_folder):
    generate_line_plot(df_all, output_folder)
    generate_heatmap(df_all, output_folder)
    generate_bar_chart(df_all, output_folder)
    print("All visualizations generated successfully.")
