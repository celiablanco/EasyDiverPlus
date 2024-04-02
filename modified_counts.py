# Script to generate modified count files
# Requires bash file modified_counts_bash.sh

from time import time
import sys
import os
import re
import glob
import fnmatch

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
            return f"[{max(result[0] - result[1], 1)}, {result[0] + result[1]}]" # Min abundance is 1
    else:
        if result[0] == 0 and result[1] == 0: # We did not observe this
            return "[0.000000, 0.000000]"
        else:
            return f"[{(max(result[0] - result[1], 0.000001)):.6f}, {(result[0] + result[1]):.6f}]"

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

def run_enrichment_analysis(out_file, in_file=None, res_file=None, neg_file=None):
    start = time()

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
        f_post_boot = [f_post, f_post - (c_post_boot[0] - c_post_boot[1]) / float(totals[2])]
        c_in_boot = bootstrap(c_in, totals[0])
        f_in_boot = [f_in, f_in - (c_in_boot[0] - c_in_boot[1]) / float(totals[0])]
        c_neg_boot = None
        f_neg_boot = None

        print(str(seq).ljust(max_len), end='\t', file=out)
        print(str(c_in_boot[0]).ljust(10), end='\t', file=out)
        print(format_bootstrap(c_in_boot, 'a').ljust(15), end='\t', file=out)
        print(str(f"{f_in_boot[0]:.6f}").ljust(10), end='\t', file=out)
        print(format_bootstrap(f_in_boot, 'f').ljust(15), end='\t', file=out)
        print(str(c_post_boot[0]).ljust(10), end='\t', file=out)
        print(format_bootstrap(c_post_boot, 'a').ljust(15), end='\t', file=out)
        print(str(f"{f_post_boot[0]:.6f}").ljust(10), end='\t', file=out)
        print(format_bootstrap(f_post_boot, 'f').ljust(15), end='\t', file=out)

        if neg_file is not None:
            c_neg_boot = bootstrap(c_neg, totals[1])
            f_neg_boot = [f_neg, f_neg - (c_neg_boot[0] - c_neg_boot[1]) / float(totals[1])]
            print(str(c_neg_boot[0]).ljust(10), end='\t', file=out)
            print(str(format_bootstrap(c_neg_boot, 'a')).ljust(15), end='\t', file=out)
            print(str(f"{f_neg_boot[0]:.6f}").ljust(10), end='\t', file=out)
            print(format_bootstrap(f_neg_boot, 'f').ljust(15), end='\t', file=out)

        # !!! Calculate and adjust enrichment in positive and negative pools
        if f_in_boot[0] + f_in_boot[1] > 0: # If the max is more than 1, we've set the min to more than 1
            enr_post_min = max(0, (f_post_boot[0] - f_post_boot[1])) / (f_in_boot[0] + f_in_boot[1])  # Min enrichment due to selection - assumes smallest f_out and largest f_in
            enr_post_max = max(0, (f_post_boot[0] + f_post_boot[1])) / max(f_in_boot[0] - f_in_boot[1], 0.000001)
            enr_neg_min = max(0, (f_neg_boot[0] - f_neg_boot[1])) / (f_in_boot[0] + f_in_boot[1])
            enr_neg_max = max(0, (f_neg_boot[0] + f_neg_boot[1])) / max(f_in_boot[0] - f_in_boot[1], 0.000001)
        else: # Not enough data to make an estimate
            enr_post_min = 0
            enr_post_max = 0
            enr_neg_min = 0
            enr_neg_max = 0

        if enr_post_max > 0: # Makes sense to print enr_post
            enr_post = f_post_boot[0] / f_in_boot[0]
            print(str(f"{enr_post:.6f}").ljust(10), end='\t\t', file=out)
            print(str(f"[{enr_post_min:.6f}, {enr_post_max:.6f}]").ljust(15), end='\t\t', file=out)
        else:
            print('-'.ljust(15), end='\t\t', file=out)

        if neg_file is not None: # 2A, 2B case check
            if enr_neg_max > 0:
                enr_neg_min = max(0.000001, enr_neg_min)    # min of 0.000001 To make the enr ratio calculatable
                enr_neg = f_neg_boot[0] / f_in_boot[0]
                print(str(f"{enr_neg:.6f}").ljust(10), end='\t\t', file=out)
                print(str(f"[{enr_neg_min:.6f}, {enr_neg_max:.6f}]").ljust(15), end='\t\t', file=out)
            else:
                print('-'.ljust(15), end='\t\t', file=out)

        if enr_neg_max > 0 and enr_neg_min > 0:
            enr_ratio_min = max(0.000001, enr_post_min / enr_neg_max) # min of 0.000001 just in case
            enr_ratio_max = enr_post_max / enr_neg_min
            # enr_ratio_bootstrap = bootstrap(enr_post_boot, 1)
            print(str(f"{enr_post / enr_neg:.6f}").ljust(10), end='\t\t', file=out)
            print(str(f"[{enr_ratio_min:.6f}, {enr_ratio_max:.6f}]").ljust(15), end='\n', file=out)
        elif neg_file is None:
            print(' '.ljust(15), file=out)
        else:
            print('-'.ljust(15), file=out)

    out.close()
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

    print(counts_type)
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
                run_enrichment_analysis(out_file=glob.glob(os.path.join(counts_dir, str(i) + "-out*" + "_" + counts_type + ".txt")), res_file=f"modified_counts/{i}-res.txt")
            else:
                run_enrichment_analysis(out_file=glob.glob(os.path.join(counts_dir, str(i) + "-out*" + "_" + counts_type + ".txt")), neg_file=glob.glob(os.path.join(counts_dir, str(i + 1) + "-neg*" + "_" + counts_type + ".txt")), res=glob.glob(os.path.join(outdir, "modified_counts", str(i) + "-res.txt")))
            
            # Calculate progress
            progress = i * 100 / (max_round - 1)
            print(f"(Approx.) Progress: {progress}%")
    else:
        # Case 2A and 2B: Loop up to max_round
        for i in range(1, max_round + 1):
            # Run the modified_counts_bash.sh script with the appropriate arguments
            neg_files_exist = any(fnmatch.fnmatch(file, neg_format) for file in os.listdir(counts_dir))
            if not neg_files_exist:
                run_enrichment_analysis(out_file=glob.glob(os.path.join(counts_dir, str(i) + "-out*" + "_" + counts_type + ".txt"))[0], in_file=glob.glob(os.path.join(counts_dir, str(i) + "-in*" + "_" + counts_type + ".txt")[0], res_file=f"modified_counts/{i}-res.txt"))
            else:
                run_enrichment_analysis(out_file=glob.glob(os.path.join(counts_dir, str(i) + "-out*" + "_" + counts_type + ".txt"))[0], in_file=glob.glob(os.path.join(counts_dir, str(i) + "-in*" + "_" + counts_type + ".txt"))[0], neg_file=glob.glob(os.path.join(counts_dir, str(i) + "-neg*" + "_" + counts_type + ".txt"))[0], res_file=f"{os.path.join(outdir, 'modified_counts', str(i) + '-res.txt')}")

        progress = i * 100 / max_round
        print("(Approx.) Progress:", progress, "%")


if __name__ == '__main__':
    find_enrichments()