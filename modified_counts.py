# Script to generate modified count files
# Requires bash file modified_counts_bash.sh

from time import time
import sys
import os
import my_sequences
import re

from bootstrap import bootstrap


# data_dir = "data"
# os.chdir(data_dir)

# Helper function to format the bootstrap result as a string with a fixed width of 15 characters
# Note: The bootstrap format is [MEAN/OBSERVED VALUE, DISTANCE TO LOWER OR UPPER BOUND OF 95 CONFIDENCE INTERVAL (CI)]
def format_bootstrap(result, type):
    if type == 'a': # For abundances
        if result[0] == 0 and result[1] == 0: # We did not observe this
            return "[0, 0]"
        else:
            return f"[{result[0]}, {result[1]}]"
    else:
        if result[0] == 0 and result[1] == 0: # We did not observe this
            return "[0.000000, 0.000000]"
        else:
            return f"[{result[0]:.6f}, {result[1]:.6f}]"

# Helper function for multi-round cases (1A + 1B) to find the prefix for the next round and then find the file associated
def next_round_file(input_str):
    # Find the index of the last slash in the string to isolate the directory path
    last_slash_index = input_str.rfind('/')
    directory = input_str[:last_slash_index + 1] if last_slash_index != -1 else ''

    # Use regular expression to find the number before "-out[whatever].txt" in the filename
    match = re.search(r'(\d+)-out.*\.txt$', input_str)
    if match:
        number = int(match.group(1))  # Extract the integer part
        incremented_number = str(number + 1)  # Increment the integer and convert it back to string
        file_pre = incremented_number + '-out'
        # return file_pre # directory_path + input_str[last_slash_index + 1:].replace(match.group(0), new_filename)
    else:
        return None # No match found

    for file in os.listdir(directory):
        if file.startswith(file_pre) and file.endswith('.txt'):
            return os.path.join(directory, file) # directory + input_str[last_slash_index + 1:].replace(match.group(0), file)
    return None


start = time()

in_file = None
neg_file = None
out_file = None
res_file = None

# Parse command-line arguments
i = 1
while i < len(sys.argv):
    if sys.argv[i] == "-in" and i + 1 < len(sys.argv):
        in_file = sys.argv[i + 1]
        i += 2
    elif sys.argv[i] == "-neg" and i + 1 < len(sys.argv):
        neg_file = sys.argv[i + 1]
        i += 2
    elif sys.argv[i] == "-out" and i + 1 < len(sys.argv):
        out_file = sys.argv[i + 1]
        i += 2
    elif sys.argv[i] == "-res" and i + 1 < len(sys.argv):
        res_file = sys.argv[i + 1]
        i += 2
    else:
        print("Invalid arguments provided.")
        sys.exit(1)

# Check if at least out_file is provided
if out_file is None:
    print("Please provide the post-selection file.")
    sys.exit(1)

# Set default output file name if not provided
if res_file is None:
    res_file = "results.txt"

if not os.path.exists(os.path.split(res_file)[0]):
    os.makedirs(os.path.split(res_file)[0])

# Cases 1A and 1B, no separate in file
if in_file is None:
    if neg_file is None:
        print("Now computing enrichments for Case 1A...")
    else:
        print("Now computing enrichments for Case 1B...")
    in_file = out_file # Treat current out file as the input file for the next round
    out_file = next_round_file(in_file) # ex: If the file is named 9-out.txt, the next_round_file is named 10-out.txt
    if not os.path.exists(out_file) or neg_file is not None and not os.path.exists(neg_file):
        print("Hmm... it seems as if there is no out file after this one. Would you like to specify an in file?")
        if not os.path.exists(neg_file):
            print("There is no round for neg control after the provided file.")
        sys.exit(1)

current_dir = os.getcwd()  # Debugging purposes
print("The current directory is: " + current_dir)

files = [in_file, neg_file, out_file]
print("Files being processed [in, neg, out]:" + str(files))
files_exist = [file is not None and os.path.exists(file) for file in files]

all_dict = []
totals = [] # in, neg, and then out total, respectively
uniques = []
max_len = 0
for i, in_file in enumerate(files):
    seqs = []
    abunds = []
    fracs = []
    if not files_exist[i]:
        continue
    with open(in_file) as in_data:
        unique_line = next(in_data)
        total_line = next(in_data)
        unique = int(unique_line.split('=')[1])
        total = int(total_line.split('=')[1])
        totals.extend([total])
        uniques.extend([unique])
        next(in_data)
        for line in in_data:
            seq = line.split()[0]
            abund = int(line.split()[1])
            frac = abund / float(total)
            seqs.extend([seq])
            abunds.extend([abund])
            fracs.extend([frac])
            if len(seq) > max_len:
                max_len = len(seq)
        seqfit_list = [[seqs[i], (abunds[i], fracs[i])] for i in range(len(seqs))]
        seqfit_dict = dict(seqfit_list)
        all_dict.append(seqfit_dict)

print("Max length sequence:", max_len)

out = open(res_file,'w')
print(str('number of unique sequences = ') + str(uniques[-1]), file=out) # Changed to -1
print(str('total number of molecules = ') + str(totals[-1]), end='\n', file=out)
if in_file is not None:
    print(str('number of unique sequences (input) = ') + str(uniques[0]), file=out)
    print(str('total number of molecules (input) = ') + str(totals[0]), end='\n', file=out)
if neg_file is not None:
    print(str('number of unique sequences (neg control) = ') + str(uniques[1]), file=out)
    print(str('total number of molecules (neg control) = ') + str(totals[1]), end='\n', file=out)

print(str('seq').ljust(max_len), end='\t', file=out)
print(str('a_in').ljust(5), end='\t\t', file=out)
print(str('a_in (95 CI)').ljust(5), end='\t\t', file=out)
print(str('f_in').ljust(5), end='\t\t', file=out)
print(str('f_in (95 CI)').ljust(10), end='\t\t', file=out)
print(str(str('a_out')).ljust(5), end='\t\t', file=out)
print(str('a_out (95 CI)').ljust(10), end='\t\t', file=out)
print(str(str('f_out')).ljust(10), end='\t\t', file=out)
print(str(str('f_out (95 CI)')).ljust(10), end='\t\t', file=out)
if neg_file is not None:
    print(str(str('a_neg')).ljust(5), end='\t\t', file=out)
    print(str(str('a_neg (95 CI)')).ljust(10), end='\t\t', file=out)
    print(str(str('f_neg')).ljust(10), end='\t\t', file=out)
    print(str(str('f_neg (95 CI)')).ljust(10), end='\t\t', file=out)
    print(str(str('e_out')).ljust(10), end='\t\t', file=out)
    print(str(str('e_out (interval)')).ljust(10), end='\t\t', file=out)
if neg_file is not None:
    print(str(str('e_n')).ljust(10), end='\t\t', file=out)
    print(str(str('e_n (interval)')).ljust(10), end='\t\t', file=out)
    print(str(str(str('e_out')) + ("/") + str(str('e_n'))).ljust(10), end='\t\t', file=out)
    print(str(str(str('e_out')) + ("/") + str(str('e_n (interval)'))).ljust(10), end='\n', file=out)
else:
    print("\n")

for seq in all_dict[-1]: # Originally 2. Calculate each sequence's a_in, f_in, a_out, etc. stats
    f_post = all_dict[-1][seq][1]
    c_post = all_dict[-1][seq][0]

    try:
        f_in = all_dict[0][seq][1]
        c_in = all_dict[0][seq][0]

    except KeyError:
        f_in = 0  # Change this line to modify fraction used if not found
        c_in = 0
    if neg_file is not None:
        try:
            f_neg = all_dict[1][seq][1]
            c_neg = all_dict[1][seq][0]
        except KeyError:
            f_neg = 0
            c_neg = 0
    else:
        f_neg = 0
        c_neg = 0

    # Bootstrap data !!! Changed this part to make freq ranges make more sense according to abundances
    c_post_boot = bootstrap(c_post, totals[2])
    c_in_boot = bootstrap(c_in, totals[0])
    c_neg_boot = None

    c_post_range = [0, 0] if c_post == 0 else [max(c_post - c_post_boot[1], 1), c_post + c_post_boot[1]]
    f_post_range = [(x / float(totals[2])) for x in c_post_range]
    c_in_range = [0, 0] if c_in == 0 else [max(c_in - c_in_boot[1], 1), c_in + c_in_boot[1]]
    f_in_range = [(x / float(totals[0])) for x in c_in_range]

    # Write data to file
    if seq in my_sequences.seq_nicknames:
        print(str(my_sequences.seq_nicknames[seq]).ljust(max_len), end='\t', file=out)
        print("Found \"" + my_sequences.seq_nicknames[seq] + "\" " + format_bootstrap(c_post_range, 'a') + " times with " + format_bootstrap(f_post_range, 'f') + " frequency.")
    else:
        print(str(seq).ljust(max_len), end='\t', file=out)
    print(str(c_in).ljust(10), end='\t', file=out)
    print(format_bootstrap(c_in_range, 'a').ljust(15), end='\t', file=out)
    print(str(f"{f_in:.6f}").ljust(10), end='\t', file=out)
    print(format_bootstrap(f_in_range, 'f').ljust(15), end='\t', file=out)
    print(str(c_post).ljust(10), end='\t', file=out)
    print(format_bootstrap(c_post_range, 'a').ljust(15), end='\t', file=out)
    print(str(f"{f_post:.6f}").ljust(10), end='\t', file=out)
    print(format_bootstrap(f_post_range, 'f').ljust(15), end='\t', file=out)

    if neg_file is not None:
        c_neg_boot = bootstrap(c_neg, totals[1])
        c_neg_range = [0, 0] if c_neg == 0 else [max(c_neg - c_neg_boot[1], 1), c_neg + c_neg_boot[1]]
        f_neg_range = [(x / float(totals[2])) for x in c_neg_range]
        print(str(c_neg).ljust(10), end='\t', file=out)
        print(str(format_bootstrap(c_neg_range, 'a')).ljust(15), end='\t', file=out)
        print(str(f"{f_neg:.6f}").ljust(10), end='\t', file=out)
        print(format_bootstrap(f_neg_range, 'f').ljust(15), end='\t', file=out)

    # !!! Calculate and adjust enrichment in positive and negative pools
    if f_in_range[0] > 0: # If the max is more than 1, we've set the min to more than 1
        enr_post_min = f_post_range[0] / f_in_range[1]  # Min enrichment due to selection - assumes smallest f_out and largest f_in
        enr_post_max = f_post_range[1] / f_in_range[0]  # Max enrichment due to selection - assumes largest f_out and smallest f_in
        enr_neg_min = f_neg_range[0] / f_in_range[1]
        enr_neg_max = f_neg_range[1] / f_in_range[0]
    else: # Not enough data to make an estimate
        enr_post_min = 0
        enr_post_max = 0
        enr_neg_min = 0
        enr_neg_max = 0

    if enr_post_max > 0: # Makes sense to print enr_post
        enr_post = f_post / f_in
        print(str(f"{enr_post:.6f}").ljust(10), end='\t\t', file=out)
        print(str(f"[{enr_post_min:.6f}, {enr_post_max:.6f}]").ljust(15), end='\t\t', file=out)
    else:
        print('-'.ljust(15), end='\t\t', file=out)

    if neg_file is not None: # 2A, 2B case check
        if enr_neg_max > 0:
            enr_neg = f_neg / f_in
            print(str(f"{enr_neg:.6f}").ljust(10), end='\t\t', file=out)
            print(str(f"[{enr_neg_min:.6f}, {enr_neg_max:.6f}]").ljust(15), end='\t\t', file=out)
        else:
            print('-'.ljust(15), end='\t\t', file=out)

    if enr_neg_max > 0 and enr_neg_min > 0:
        enr_ratio_min = enr_post_min / enr_neg_max
        enr_ratio_max = enr_post_max / enr_neg_min
        print(str(f"{enr_post / enr_neg:.6f}").ljust(10), end='\t\t', file=out)
        print(str(f"[{enr_ratio_min:.6f}, {enr_ratio_max:.6f}]").ljust(15), end='\n', file=out)
    elif neg_file is None:
        print(' '.ljust(15), file=out)
    else:
        print('-'.ljust(15), file=out)

out.close()
print("Time elapsed: " + str(time() - start) + ' s')


