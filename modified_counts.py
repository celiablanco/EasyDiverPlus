# Script to generate modified count files
# Requires bash file modified_counts_bash.sh

from time import time
import sys
import os
import re
import glob
import fnmatch
import csv

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

def base_encode(num, chars):
    if num == 0:
        return chars[0]
    encoded = []
    while num > 0:
        num, rem = divmod(num, len(chars))
        encoded.insert(0, chars[rem])
    return ''.join(encoded)

def run_enrichment_analysis(out_file, in_file=None, res_file=None, neg_file=None):
    start = time()

    # Check if at least out_file is provided
    if out_file is None:
        print("Please provide the post-selection file.")
        sys.exit(1)

    # Set default output file name if not provided
    if res_file is None:
        res_file = "results.csv"

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
            print(f"Total Line: {total_line.split('=')[1]}")
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

    with open(res_file, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)

        # Write general information
        writer.writerow(['Number of Unique Sequences', uniques[-1]])
        writer.writerow(['Total Number of Molecules', totals[-1]])
        if in_file is not None:
            writer.writerow(['Number of Unique Sequences (Input)', uniques[0]])
            writer.writerow(['Total Number of Molecules (Input)', totals[0]])
        if neg_file is not None:
            writer.writerow(['Number of Unique Sequences (Neg Control)', uniques[1]])
            writer.writerow(['Total Number of Molecules (Neg Control)', totals[1]])

        # Write column headers
        writer.writerow(['unique_name', 'seq', 'a_in', 'a_in (95 CI)', 'f_in', 'f_in (95 CI)', 'a_out', 'a_out (95 CI)', 'f_out', 'f_out (95 CI)', 'a_neg', 'a_neg (95 CI)', 'f_neg', 'f_neg (95 CI)', 'e_out', 'e_out (interval)', 'e_n', 'e_n (interval)', 'e_out/e_n', 'e_out/e_n (interval)'])

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

    # Write data to the CSV file
        unique_sequences = {}
        seq_names = all_dict[-1].keys()
        sequence_number = 0
        chars58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

        for seq in seq_names:
            row = []
            if seq in unique_sequences.keys():
                print("Found \"" + seq + "\" " + format_bootstrap(c_post_range, 'a') + " times with " + format_bootstrap(f_post_range, 'f') + " frequency.")
            else:
                seq_name_base58 = base_encode(sequence_number, chars58)
                unique_sequences[seq] = seq_name_base58
                sequence_number += 1
                row.append(f"seq_{unique_sequences[seq]}")
                row.append(seq)
                row.append(str(c_in))
                row.append(format_bootstrap(c_in_range, 'a'))
                row.append(str(f"{f_in:.6f}"))
                row.append(format_bootstrap(f_in_range, 'f'))
                row.append(str(c_post))
                row.append(format_bootstrap(c_post_range, 'a'))
                row.append(str(f"{f_post:.6f}"))
                row.append(format_bootstrap(f_post_range, 'f'))

                if neg_file is not None:
                    c_neg_boot = bootstrap(c_neg, totals[1])
                    c_neg_range = [0, 0] if c_neg == 0 else [max(c_neg - c_neg_boot[1], 1), c_neg + c_neg_boot[1]]
                    f_neg_range = [(x / float(totals[2])) for x in c_neg_range]
                    row.append(str(c_neg))
                    row.append(str(format_bootstrap(c_neg_range, 'a')))
                    row.append(str(f"{f_neg:.6f}"))
                    row.append(format_bootstrap(f_neg_range, 'f'))

                # Calculate and adjust enrichment in positive and negative pools
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
                    row.append(str(f"{enr_post:.6f}"))
                    row.append(str(f"[{enr_post_min:.6f}, {enr_post_max:.6f}]"))
                else:
                    row.append('-')

                if neg_file is not None: # 2A, 2B case check
                    if enr_neg_max > 0:
                        enr_neg = f_neg / f_in
                        row.append(str(f"{enr_neg:.6f}"))
                        row.append(str(f"[{enr_neg_min:.6f}, {enr_neg_max:.6f}]"))
                    else:
                        row.append('-')

                if enr_neg_max > 0 and enr_neg_min > 0:
                    enr_ratio_min = enr_post_min / enr_neg_max
                    enr_ratio_max = enr_post_max / enr_neg_min
                    row.append(str(f"{enr_post / enr_neg:.6f}"))
                    row.append(str(f"[{enr_ratio_min:.6f}, {enr_ratio_max:.6f}]"))
                elif neg_file is None:
                    row.append(' ')
                else:
                    row.append('-')
                
                writer.writerow(row)

    print("Time elapsed: " + str(time() - start) + ' s')

def find_enrichments():
    counts_type = ""
    # Parse command-line arguments
    print("Parsing arguments\n")
    print(sys.argv)
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "-dir" and i + 1 < len(sys.argv):
            dir_path = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "-out" and i + 1 < len(sys.argv):
            i += 2
        elif sys.argv[i] == "-count" and i + 1 < len(sys.argv):
            counts_type = sys.argv[i + 1]
            i += 2
        else:
            print("Invalid arguments provided.")
            sys.exit(1)

    if dir_path is None:
        print("Directory path not provided.")
        sys.exit(1)

    # Set directory path
    outdir = dir_path
    counts_dir = os.path.join(outdir, counts_type)

    print(f"Current directory path: {counts_dir}")

    # Get the maximum round
    max_round = 0
    for file in os.listdir(counts_dir):
        if "-out" in file and counts_type in file:
            round_num = int(file.split("-out")[0])
            if round_num > max_round:
                max_round = round_num
    progress = 5
    print("(Approx.) Progress:", progress, "%")

    in_format = f"*-in*_{counts_type}.txt"
    neg_format = f"*-neg*_{counts_type}.txt"

    # Check if there are any files matching the format "*-in*_counts.txt"
    if not any(fnmatch.fnmatch(file, in_format) for file in os.listdir(counts_dir)):
        # Cases 1A and 1B: Loop up to max_round - 1
        for i in range(1, max_round):
            # Run the modified_counts_bash.sh script with the appropriate arguments
            neg_files_exist = any(fnmatch.fnmatch(file, neg_format) for file in os.listdir(counts_dir))
            if not neg_files_exist:
                run_enrichment_analysis(out_file=glob.glob(os.path.join(counts_dir, str(i) + "-out*" + "_" + counts_type + ".txt")), res_file=f"modified_counts/{i}-res.csv")
            else:
                run_enrichment_analysis(out_file=glob.glob(os.path.join(counts_dir, str(i) + "-out*" + "_" + counts_type + ".txt")), neg_file=glob.glob(os.path.join(counts_dir, str(i + 1) + "-neg*" + "_" + counts_type + ".txt")), res=glob.glob(os.path.join(outdir, "modified_counts", str(i) + "-res.csv")))
            
            # Calculate progress
            progress = i * 100 / (max_round - 1)
            print(f"(Approx.) Progress: {progress}%")
    else:
        # Case 2A and 2B: Loop up to max_round
        for i in range(1, max_round + 1):
            # Run the modified_counts_bash.sh script with the appropriate arguments
            neg_files_exist = any(fnmatch.fnmatch(file, neg_format) for file in os.listdir(counts_dir))
            if not neg_files_exist:
                run_enrichment_analysis(out_file=glob.glob(os.path.join(counts_dir, str(i) + "-out*" + "_" + counts_type + ".txt"))[0], in_file=glob.glob(os.path.join(counts_dir, str(i) + "-in*" + "_" + counts_type + ".txt")[0], res_file=f"modified_counts/{i}-res.csv"))
            else:
                run_enrichment_analysis(out_file=glob.glob(os.path.join(counts_dir, str(i) + "-out*" + "_" + counts_type + ".txt"))[0], in_file=glob.glob(os.path.join(counts_dir, str(i) + "-in*" + "_" + counts_type + ".txt"))[0], neg_file=glob.glob(os.path.join(counts_dir, str(i) + "-neg*" + "_" + counts_type + ".txt"))[0], res_file=f"{os.path.join(outdir, 'modified_counts', str(i) + '-res.csv')}")

        progress = i * 100 / max_round
        print("(Approx.) Progress:", progress, "%")


if __name__ == '__main__':
    find_enrichments()
