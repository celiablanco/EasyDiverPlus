#!/usr/bin/env python3

import pandas as pd
import re
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment
import sys

# Read the text file
input_file = sys.argv[1]
line_limit = 1000 # up to 1,000,000
# input_file = "data/output/modified_counts/2-res.txt"
data = []
with open(input_file, "r", encoding="utf-8") as file:
    i = 0
    for line in file:
        if (i == line_limit):
            break
        line_data = re.split(r'\t+', line.strip())
        data.append(line_data)
        i += 1

# Create a DataFrame from the parsed data
columns = ["col1", "col2", "col3", "col4", "col5", "col6", "col7", "col8", "col9", "col10", "col11", "col12", "col13", "col14", "col15", "col16", "col17", "col18", "col19"]
df = pd.DataFrame(data, columns=columns)

# Specify the even columns that should be converted to numeric
even_columns = ["col2", "col4", "col6", "col8", "col10", "col12", "col14", "col16", "col18"]

# Convert even columns to numeric only after the header line
df.loc[7:, even_columns] = df.loc[7:, even_columns].apply(pd.to_numeric, errors='coerce')

# Specify the output Excel file
output_file = 'figures/' + input_file.split('/')[-1].split('.')[0] + '.xlsx'  # Excel file named accordingly
#
# Save DataFrame to Excel
df.to_excel(output_file, index=False)

# Open the Excel file
wb = load_workbook(filename=output_file)
ws = wb.active

# Set column width for each column
column_widths = [50, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20]  # Adjust these values as needed
for i, column in enumerate(columns):
    ws.column_dimensions[chr(65 + i)].width = column_widths[i]

# Save the modified Excel file
wb.save(output_file)