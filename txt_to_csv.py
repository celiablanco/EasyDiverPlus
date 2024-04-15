import csv
import sys

input_file = sys.argv[1]

# Open input file
with open(input_file, 'r') as txt_file:
    lines = txt_file.readlines()

# Column names
fieldnames = ["seq", "a_in", "a_in (95 CI)", "f_in", "f_in (95 CI)", "a_out", "a_out (95 CI)", "f_out", "f_out (95 CI)",
    "a_neg", "a_neg (95 CI)", "f_neg", "f_neg (95 CI)", "e_out", "e_out (interval)", "e_n", "e_n (interval)",
    "e_out/e_n", "e_out/e_n (interval)"]

# Append data line by line
data = []
for line in lines:
    row = line.strip().split('\t')
    data.append(row)

# Write the data into a CSV file
with open('output.csv', 'w', newline='') as csv_file:
    writer = csv.writer(csv_file)

    # Write metrics
    for i, row in enumerate(data):
        if len(row) > 1:
            row_idx = i
            break

        writer.writerow(row)

    # Write default headers
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()

    # Write row data
    for row in data[row_idx+1:]:
        data = {}
        for i in range(len(fieldnames)):
            if i < len(row):
                data[fieldnames[i]] = row[i].strip()
            else:
                data[fieldnames[i]] = "-"

        writer.writerow(data)