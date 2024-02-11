#!/usr/bin/env python3

"""
graphs.py plots a histogram for sequence length, a scatterplot comparing enrichment values, and a line chart showing
total and unique AA counts over time.
"""
import os
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import re
import sys

file_path = sys.argv[1] # "scripts_enrichments/res.txt", "output_large"
graph = sys.argv[2] # Selection between 1 (scatterplot), 2 (histogram), and 3 (AA counts)


"""
   This function removes outliers from the given x and y values based on the provided z-score threshold.
    Used to graph scatterplot.
   Parameters:
   x_values (list): A list of x-values from which outliers are to be removed.
   y_values (list): A list of y-values from which outliers are to be removed.
   zscore_threshold (int): The z-score threshold to identify an outlier. Default is 3.

   Returns:
   x_values_filtered (numpy array): The filtered x-values after removing outliers.
   y_values_filtered (numpy array): The filtered y-values after removing outliers.
"""
def remove_outliers(x_values, y_values, zscore_threshold=3):
    # Calculate Z-scores for x and y
    x_zscores = np.abs((x_values - np.mean(x_values)) / np.std(x_values))
    y_zscores = np.abs((y_values - np.mean(y_values)) / np.std(y_values))

    # Create a mask to filter outlier points
    outlier_mask = (x_zscores <= zscore_threshold) & (y_zscores <= zscore_threshold)

    # Apply the mask to keep only non-outlier points
    x_values_filtered = np.array(x_values)[outlier_mask]
    y_values_filtered = np.array(y_values)[outlier_mask]

    return x_values_filtered, y_values_filtered

# Set seaborn style
sns.set(style="darkgrid")

# Scatterplot
if graph == "1":
    e_out_values = []
    e_neg_values = []

    with open(file_path, 'r') as file:
        lines = file.readlines()
        start = 7 # Hard-coded
        for line in lines[start:]:
            # Split the line by whitespace to get individual columns
            columns = line.split()
            if "-" in (columns[-3], columns[-4], columns[-5], columns[-6]):
                continue
            # Calculate the measured e_out and e_neg values and convert them to float
            e_out = (float(re.sub(r'[^\d.]', '', columns[-5])) + float(re.sub(r'[^\d.]', '', columns[-6]))) / 2
            e_neg = (float(re.sub(r'[^\d.]', '', columns[-3])) + float(re.sub(r'[^\d.]', '', columns[-4]))) / 2
            # Append the values to their respective lists
            e_out_values.append(e_out)
            e_neg_values.append(e_neg)

    # Plotting the scatter plot
    x_filtered, y_filtered = remove_outliers(e_neg_values, e_out_values)
    plt.scatter(x_filtered, y_filtered, s=10)
    plt.plot(x_filtered, x_filtered, color='blue', linestyle='dotted', linewidth=1)

    # Adding labels and title
    plt.xlabel('e_neg')
    plt.ylabel('e_out')
    plt.title('e_neg vs e_out Scatter Plot')
    plt.savefig("figures/" + file_path[file_path.rfind("/") + 1:file_path.rfind(".")] + ".png", dpi=500)
    # Show the plot
    # plt.show()
    plt.close()

# Histogram
elif graph == "2":
    histos = os.path.join(file_path, "histos")
    files = [file for file in os.listdir(histos) if file.endswith(".txt")] # Find data for histos

    for file in files:
        filename = os.path.join(histos, file)
        lines = None
        with open(filename, 'r') as f:
            lines = f.readlines()

        lengths = []
        reads_counts = []
        start = lines.index("Len  Reads  %Reads\n") + 1 # Start line for data

        for line in lines[start:]:
            values = line.split()
            length = int(values[0])
            reads_count = int(values[1])
            lengths.append(length)
            reads_counts.append(reads_count)
        plt.figure(figsize=(12, 8))
        # Plotting the histogram without log scale
        plt.subplot(2, 1, 1)
        plt.bar(lengths, reads_counts, color="steelblue")
        plt.xlabel('Length')
        plt.ylabel('Reads Count')
        plt.title('Read Length Histogram for ' + file)

        # Plotting the histogram with log scale
        plt.subplot(2, 1, 2)
        plt.bar(lengths, reads_counts, color="steelblue")
        plt.xlabel('Length')
        plt.ylabel('Reads Count')
        plt.title('Read Length Histogram (Log Scale)')
        plt.yscale('log')  # Log scale the y-axis

        plt.tight_layout()  # Adjust spacing between subplots
        # plt.show()
        plt.savefig("figures/" + file[:file.rfind(".")] + ".png", dpi=500)
        plt.close()
# Line graph
elif graph == "3":
    file_path += "/log.txt"

    # Lists to store the data
    sample_names = []
    unique_aa = {}
    total_aa = {}
    max_round = -1
    # Read the text file and extract the data
    with open(file_path, 'r') as file:
        lines = file.readlines()
        start = False  # Initialize a flag to identify the start of relevant data
        for line in lines:
            if line.startswith("sample"):
                start = True
                continue
            elif start:
                total_aa_ind = -1
                line_data = line.split()  # Split the line into individual data points
                if line_data[-1][-1] == '%':
                    total_aa_ind -= 1 # Solves formatting issues if recovered_aa(%) decides to print

                sample_name = line_data[0]
                sample_name_substr = sample_name.split("-")[1]

                sample_names.append(sample_name)  # Store the first data point (sample name)
                max_round = max(max_round, int(sample_name.split("-")[0]))
                # Append unique amino acid (AA) counts to a dictionary, using the AA type as the key
                # The second-to-last data point ([-2]) is the count of unique AAs
                unique_aa.setdefault(sample_name_substr[0:sample_name_substr.find("_")], []).append(int(line_data[total_aa_ind - 1]))  # TODO: Don't hardcode?
                # Append total AA counts to a dictionary, using the AA type as the key
                # The last data point ([-1]) is the count of total AAs
                total_aa.setdefault(sample_name_substr[0:sample_name_substr.find("_")], []).append(int(line_data[total_aa_ind]))

    print("Unique amino acid (AA) counts throughout rounds: " + str(unique_aa))
    print("Total amino acid (AA) counts throughout rounds: " + str(total_aa))
    # Create a figure for plotting
    plt.figure(figsize=(10, 6))

    # Iterate through different AA types
    for key in unique_aa.keys():
        color = "orange"
        if key == "neg":
            color = "green"
        elif key == "in":
            color = "red"
        label_u = "Unique AA " + key
        label_t = "Total AA " + key
        # Plot the unique AA counts and label with the AA type
        plt.plot(unique_aa[key], marker="o", label=label_u, color=color)
        # Plot the total AA counts and label with the AA type
        plt.plot(total_aa[key], marker="o", label=label_t, color="dark" + color)

    # Add labels and title to the plot
    plt.xlabel('Round')
    plt.ylabel('Count')
    plt.title('Unique and Total Amino Acid Counts Throughout Experiment')

    # Add a legend to distinguish unique and total counts for each AA type
    plt.legend()
    # Customize x-axis labels to show round numbers
    plt.xticks(range(0, max_round), [f'#{i}' for i in range(1, max_round + 1)], rotation=45)
    # Adjust layout for better appearance
    plt.tight_layout()
    # Save the plot as an image with high resolution (DPI: 500)
    plt.savefig("figures/aa.png", dpi=500)


