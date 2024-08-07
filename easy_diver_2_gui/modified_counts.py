"""
Module: mod_counts__z

This module provides a collection of functions for processing and analyzing sequence count data, 
specifically designed for use with Easy Diver counts files. 

The functionalities include safe division, MD5 hash generation, 
bootstrap resampling, binomial bootstrap sampling, data parsing, and enrichment 
analysis. The module also supports parallel processing to enhance performance on large datasets.

Functions:
    - get_first_matching_file(
        counts_dir: str,
        rounds_df: pd.DataFrame,
        file_type: str,
        round_num: int) -> str:
        Finds the first matching file in the given directory based on specified criteria.

    - safe_divide(a: float, b: float, default: float = 0.0) -> float:
        Safely divides two numbers, returning a default value in case of division by zero.

    - base_encode(sequence_number: str, input_string: str) -> str:
        Generates a shortened base58-encoded unique string for each sequence based on position

    - unique_sequence_name_generator(row: pd.Series, sequence_dict: dict) -> str:
        Either retrieves the unique sequence name from the global dictionary or 
        uses the `base_encode` function to calculate a unique string for each sequence 
        and stores it into that dictionary. 

    - bootstrap_counts_resampling(
        total_counts: int, 
        count_seq: int, 
        sequence: str, 
        bootstrap_depth: int = 1000, 
        seed: int = 42) -> tuple[str, List[float]]:
        Performs bootstrap resampling on counts data to generate confidence intervals.

    - bootstrap_counts_binomial(
        total_counts: int, 
        count_seq: int, 
        sequence: str, 
        bootstrap_depth: int = 1000, 
        seed: int = 42) -> tuple[str, List[float]]:
        Performs bootstrap binomial sampling on counts data to generate confidence intervals.

    - easy_diver_parse_file_header(filename: str) -> tuple[int, int]:
        Parses the header of an Easy Diver counts file 
        to extract the number of sequences and total molecules.

    - process_row(
        row: pd.Series, 
        total_counts: int, 
        sequence_column: str, 
        bootstrap_depth: int, 
        func: Callable) -> tuple:
        Processes a single row of a DataFrame, applying a bootstrapping function.

    - parallel_apply(
        df: pd.DataFrame, 
        func: Callable, 
        total_counts: int, 
        sequence_column: str, 
        bootstrap_depth: int) -> List:
        Applies a function to each row of a DataFrame in parallel using multiprocessing.

    - easy_diver_counts_to_df(filename: str, ed_round: int, ftype: str) -> pd.DataFrame:
        Converts an Easy Diver counts file to a pandas DataFrame, 
        including bootstrapped confidence intervals.

    - process_enrichments(row: pd.Series) -> dict:
        Calculates enrichment metrics for a single row of data.

    - merge_data_for_rounds(
        df1: pd.DataFrame, 
        df2: Optional[pd.DataFrame] = None, 
        df3: Optional[pd.DataFrame] = None, 
        include_in: bool = True, 
        include_neg: bool = True) -> pd.DataFrame:
        Merges data from different rounds into a single DataFrame.

    - enrich_and_write(round_df: pd.DataFrame, file_prefix: str, precision: int) -> bool:
        Enriches the DataFrame and writes it to a file.

    - write_enrichments_final_output(
        directory: str,
        include_negative: bool = False,
        include_in: bool = False,
        precision: int = 6) -> bool:
        Writes 'pivoted' files which have the metrics across rounds for each of the sequences.

    - find_enrichments():
        Main function to find enrichments in modified counts data 
        by running multiple rounds of processing.

This module is intended for researchers and data scientists working with sequence count data to 
perform detailed statistical analysis and enrichment studies.
"""
#!/usr/bin/python

import os
import glob
from collections import Counter
from typing import Optional
from tqdm import tqdm
import pandas as pd

def get_first_matching_file(
        counts_dir: str,
        rounds_df: pd.DataFrame,
        file_type: str,
        round_num: int) -> str:
    """
    Finds the first matching file in the given directory based on specified criteria.

    This function searches for files in the specified directory that match the provided
    file type and round number criteria from the DataFrame. It returns the first matching
    file path.

    Parameters:
    counts_dir (str): The directory where the count files are stored.
    rounds_df (pd.DataFrame): A DataFrame containing file information with columns 'file_type', 
                              'round_number', and 'filename'.
    file_type (str): The type of file to match (from the 'file_type' column of the DataFrame).
    round_num (int): The round number to match (from the 'round_number' column of the DataFrame).

    Returns:
    str: The path to the first matching file, or None if no match is found.

    Example:
    ```
    counts_dir = '/path/to/counts'
    rounds_df = pd.DataFrame({
        'file_type': ['post', 'pre', 'post', 'pre'],
        'round_number': [1, 1, 2, 2],
        'filename': ['file1', 'file2', 'file3', 'file4']
    })
    file_type = 'post'
    round_num = 1

    matching_file = get_first_matching_file(counts_dir, rounds_df, file_type, round_num)
    if matching_file:
        print(f"Found matching file: {matching_file}")
    else:
        print("No matching file found.")
    ```
    """
    filenames = rounds_df[
        (rounds_df['file_type'] == file_type) &
        (rounds_df['round_number'] == round_num)]['filename'].tolist()
    if len(filenames) == 0:
        return None
    path_pattern = os.path.join(counts_dir, filenames[0])
    matches = glob.glob(path_pattern+'*.csv')
    return matches[0] if matches else None

def check_rounds_file(rounds_df: pd.DataFrame, counts_dir: str) -> bool:
    """
    Check if the filenames in the provided DataFrame match the filenames in the specified directory.

    This function compares the filenames listed in the 'filename' column of the provided DataFrame
    to the filenames in the specified directory. The filenames in the directory are processed to 
    remove the '_counts*' suffix before comparison. If the sets of filenames match, the function 
    returns True; otherwise, it returns False.

    Parameters:
    rounds_df (pd.DataFrame): A pandas DataFrame containing 
                              a 'filename' column with the filenames to check.
    counts_dir (str): The directory path where the files to compare are located.

    Returns:
    bool: True if the filenames in the 
          DataFrame match the filenames in the directory, False otherwise.
    """
    filenames = rounds_df['filename'].tolist()
    files = [file.split('_counts')[0] for file in os.listdir(counts_dir)]
    if Counter(filenames) == Counter(files):
        return True
    return False

def safe_divide(a: float, b: float, default: float = 0.0) -> float:
    """
    Safely divides two numbers, including the case where a or b is None.

    Parameters:
    a (float): The numerator.
    b (float): The denominator.
    default (float): The value to return in case of division by zero. Default is 0.0.

    Returns:
    float: The result of the division, or the default value if division by zero occurs.
    """
    try:
        if a is None or b is None:
            return None
        return a / b
    except ZeroDivisionError:
        return default

def easy_diver_parse_file_header(file_path: str, encoding: str = 'utf-8') -> tuple[int, int]:
    """
    Parses the header of an Easy Diver counts file 
    to extract the number of sequences and total molecules.

    Parameters:
    file_path (str): The path to the counts file.
    encoding (str): The encoding for the file.

    Returns:
    tuple: A tuple containing the number of unique sequences (int) 
        and the total number of molecules (int).
    """
    with open(file_path, 'r', encoding=encoding) as file:
        # Read the first three lines of the file
        lines = [next(file).strip() for _ in range(3)]

    # Extract the values using string manipulation
    num_unique_sequences = int(lines[0].split(',')[1].strip())
    total_num_molecules = int(lines[1].split(',')[1].strip())

    return num_unique_sequences, total_num_molecules

def easy_diver_counts_to_df(filename: str, ed_round: int, ftype: str) -> pd.DataFrame:
    """
    Converts an Easy Diver counts file to a pandas DataFrame, 
    including bootstrapped confidence intervals.

    Parameters:
    filename (str): The path to the counts file.
    ed_round (int): The round number.
    ftype (str): The type of the file (e.g., 'post', 'pre', 'neg').

    Returns:
    pd.DataFrame: The DataFrame with the counts and calculated confidence intervals.
    """
    if filename is None:
        return None

    num_seqs, total_mols = easy_diver_parse_file_header(filename)
    df = pd.read_csv(
        filename,
        skiprows=4,
        header=None
    )

    df.columns = [
        'Unique_Sequence_Name','Sequence','Count',
        'Count_Lower','Count_Upper','Freq','Freq_Lower','Freq_Upper'
    ]
    df['Total_Unique_Sequences'] = num_seqs
    df['Total_Molecules'] = total_mols
    df['Round'] = ed_round
    df['Type'] = ftype
    for coln in df.columns:
        if coln.lower().startswith('freq'):
            df[coln] = df[coln].str.rstrip('%').astype('float')
    return df

def process_enrichments(row: pd.Series) -> dict:
    """
    Calculates enrichment metrics for a single row of data.

    Parameters:
    row (pd.Series): The row of data to process.

    Returns:
    dict: The calculated enrichment metrics as a dictionary, 
        to be expanded using a pandas `apply` function.
    """
    # Calculate and adjust enrichment in positive and negative pools
    include_negative = False
    if 'Count_neg' in row.index:
        include_negative = True
    if row['Freq_Lower_pre'] > 0:
        # If the max is more than 1, we've set the min to more than 1

        # Min enrichment due to selection - assumes smallest f_out and largest f_in
        enr_post_min = safe_divide(row['Freq_Lower_post'], row['Freq_Upper_pre'])

        # Max enrichment due to selection - assumes largest f_out and smallest f_in
        enr_post_max = safe_divide(row['Freq_Upper_post'], row['Freq_Lower_pre'])

        if include_negative:
            enr_neg_min = safe_divide(row['Freq_Lower_neg'], row['Freq_Upper_pre'])
            enr_neg_max = safe_divide(row['Freq_Upper_neg'], row['Freq_Lower_pre'])
        else:
            enr_neg_min = None
            enr_neg_max = None
    else:  # Not enough data to make an estimate
        enr_post_min = 0
        enr_post_max = 0
        enr_neg_min = 0
        enr_neg_max = 0

    if enr_post_max > 0:  # Makes sense to print enr_post
        enr_post = safe_divide(row['Freq_post'], row['Freq_pre'])
    else:
        enr_post = None

    if include_negative and enr_neg_max > 0:  # 2A, 2B case check
        enr_neg = safe_divide(row['Freq_neg'], row['Freq_pre'])
    else:
        enr_neg = None

    if enr_neg_max > 0 and enr_neg_min > 0:
        enr_ratio_min = safe_divide(enr_post_min, enr_neg_max)
        enr_ratio_max = safe_divide(enr_post_max, enr_neg_min)
    else:
        enr_ratio_min = None
        enr_ratio_max = None

    return {
        'Sequence': row.Sequence,
        'Enr_post': enr_post,
        'Enr_post_lower': None if enr_post is None else enr_post_min,
        'Enr_post_upper': None if enr_post is None else enr_post_max,
        'Enr_neg': enr_neg,
        'Enr_neg_lower': None if enr_neg is None else enr_neg_min,
        'Enr_neg_upper': None if enr_neg is None else enr_neg_max,
        'Enr_ratio': safe_divide(enr_post, enr_neg),
        'Enr_ratio_lower': enr_ratio_min,
        'Enr_ratio_upper': enr_ratio_max
    }

def merge_data_for_rounds(
        post_df: pd.DataFrame,
        pre_df: Optional[pd.DataFrame] = None,
        neg_df: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
    """
    Merges data from different files for the 
    same round into a single DataFrame.

    Parameters:
    post_df (pd.DataFrame): The primary DataFrame, sourced from the 'post' file.
    sequence_dict (dict): The global dictionary used to hold all the unique sequence names.
    pre_df (Optional[pd.DataFrame]): The secondary DataFrame to merge, 
        sourced from the 'pre' file. Default is None.
    neg_df (Optional[pd.DataFrame]): The tertiary DataFrame to merge,
        sourced from the 'neg' file. Default is None.
    
    Returns:
    pd.DataFrame: The merged DataFrame, 
        sorted by the `out` count column, `Count_post` in descending order.
    """
    # Merge the first two DataFrames on 'Sequence' with a full join
    columns_to_keep = [
        'Unique_Sequence_Name', 'Sequence',
        'Count', 'Count_Lower', 'Count_Upper',
        'Freq', 'Freq_Lower', 'Freq_Upper',
        'Total_Unique_Sequences', 'Total_Molecules'
    ]

    if pre_df is not None:
        merged_df = pd.merge(
            post_df[columns_to_keep],
            pre_df[columns_to_keep],
            on=['Unique_Sequence_Name','Sequence'],
            how='left',
            suffixes=(f"_{post_df['Type'][0]}", f"_{pre_df['Type'][0]}")
        )
    elif neg_df is not None:
        merged_df = pd.merge(
            post_df[columns_to_keep],
            neg_df[columns_to_keep],
            on=['Unique_Sequence_Name','Sequence'],
            how='left',
            suffixes=(f"_{post_df['Type'][0]}", f"_{neg_df['Type'][0]}")
        )
    # If a third DataFrame is provided, merge it as well with a full join
    if neg_df is not None and pre_df is not None:
        merged_df = pd.merge(
            merged_df,
            neg_df[columns_to_keep],
            on=['Unique_Sequence_Name','Sequence'],
            how='left',
            suffixes=('', f"_{neg_df['Type'][0]}")
        )
        # ensure the remaining columns have '_neg' suffix
        merged_df.columns = [
            col+'_neg'
            if col not in ('Sequence','Unique_Sequence_Name') and col in post_df.columns
            else col
            for col in merged_df.columns
        ]
    else:
        merged_df = post_df[columns_to_keep]
        # ensure the columns of the single df have '_post' suffix
        merged_df.columns = [
            col+'_post' if col not in ('Sequence','Unique_Sequence_Name') and col in post_df.columns
            else col
            for col in merged_df.columns
        ]

    sorted_df = merged_df.sort_values(by = 'Count_post', ascending = False)

    # Move the 'Unique_Sequence_Name' column to the first position
    other_cols = [
        col
        for col in sorted_df.columns
        if col != 'Unique_Sequence_Name'
    ]
    cols = ['Unique_Sequence_Name'] + other_cols
    sorted_df = sorted_df[cols]

    # if the negative or in dataframe are not present,
    # we will ensure those columns exist and
    # fill them with NaN
    for group in ['neg','pre']:
        if f"Count_{group}" not in sorted_df.columns:
            for col in [
                'Count', 'Count_Lower', 'Count_Upper',
                'Freq', 'Freq_Lower', 'Freq_Upper',
                'Total_Unique_Sequences' , 'Total_Molecules'
            ]:
                sorted_df[f"{col}_{group}"] = pd.NA

    # Reset the index to remove the actual numbered index
    sorted_df = sorted_df.reset_index(drop=True)

    # uncomment this line and change '0' to whatever
    # you want it to be (such as `-` or `*` or whatever)!
    # sorted_df.fillna(0, inplace=True)

    return sorted_df

def enrich_and_write (
        round_df: pd.DataFrame,
        file_prefix: str,
        precision: int,
        include_negative: bool = True) -> bool:
    """
    Calculates the enrichments for the joined data and writes it to a file.

    Parameters:
    round_df (pd.DataFrame): The DataFrame to enrich.
    file_prefix (str): The file prefix for the output files.
    precision (int): The precision for the output data.

    Returns:
    bool: True if the file was written successfully, False otherwise.
    """
    if not os.path.exists(os.path.split(file_prefix)[0]):
        os.makedirs(os.path.split(file_prefix)[0])
    if include_negative is True:
        final_columns = [
            'Unique_Sequence_Name','Sequence',
            'Count_pre','Count_Lower_pre','Count_Upper_pre',
            'Freq_pre','Freq_Lower_pre','Freq_Upper_pre',
            'Count_post','Count_Lower_post','Count_Upper_post',
            'Freq_post','Freq_Lower_post','Freq_Upper_post',
            'Count_neg','Count_Lower_neg','Count_Upper_neg',
            'Freq_neg','Freq_Lower_neg','Freq_Upper_neg',
            'Enr_post','Enr_post_lower','Enr_post_upper',
            'Enr_neg','Enr_neg_lower','Enr_neg_upper',
            'Enr_ratio','Enr_ratio_lower','Enr_ratio_upper'
        ]
    else:
        final_columns = [
            'Unique_Sequence_Name','Sequence',
            'Count_pre','Count_Lower_pre','Count_Upper_pre',
            'Freq_pre','Freq_Lower_pre','Freq_Upper_pre',
            'Count_post','Count_Lower_post','Count_Upper_post',
            'Freq_post','Freq_Lower_post','Freq_Upper_post',
            'Enr_post','Enr_post_lower','Enr_post_upper'
        ]

    enrichments_df = round_df.apply(process_enrichments, axis = 1, result_type = 'expand')
    final_df = pd.merge(round_df, enrichments_df, on = 'Sequence', how = 'inner')
    extras = {}
    for file_type in ['pre','post','neg']:
        extras[f"seq_{file_type}"] = int(
                final_df[f"Total_Unique_Sequences_{file_type}"].fillna(0).astype(int)[0]
        )
        extras[f"mol_{file_type}"] = int(
                final_df[f"Total_Molecules_{file_type}"].fillna(0).astype(int)[0]
        )

    extra_header = f"""Number of Unique Sequences (Input),{extras.get('seq_in')}
Total Number of Molecules (Pre),{extras.get('mol_in')}
Number of Unique Sequences (Post),{extras.get('seq_out')}
Total Number of Molecules (Post),{extras.get('mol_out')}
Number of Unique Sequences (Neg Control),{extras.get('seq_neg')}
Total Number of Molecules (Neg Control),{extras.get('mol_neg')}"""
    for col in final_df.columns:
        if col.startswith('Count'):
            final_df[col] = final_df[col].fillna(0)
            final_df[col] = final_df[col].astype(int)
        elif col.startswith('Freq'):
            final_df[col] = final_df[col].fillna(0)
            final_df[col] = final_df[col].apply(lambda x: f"{x:.{precision}f}%")
    try:
        final_df[final_columns].to_csv(
            file_prefix + 'temp.csv',
            index = False,
            header = True,
            float_format=f"%.{precision}f"
        )
        with open(file_prefix + 'temp.csv', 'r', encoding='utf-8') as original_file:
            original_content = original_file.read()

        # Write the new block of text and the original content to a new file
        with open(file_prefix + '.csv', 'w', encoding='utf-8') as new_file:
            new_file.write(extra_header + '\n' + original_content)
    except (OSError, IOError) as e:
        print(f"Failed writing the {file_prefix} results file. Exception encountered: {e}")
        return False
    try:
        # Remove the original CSV file
        os.remove(file_prefix + 'temp.csv')
    except (OSError, IOError) as e:
        print(f"Failed to remove the temporary file for the {file_prefix} results file process. "+
              f"Exception encountered: {e}"
        )
        return False
    return True

def write_enrichments_final_output(
        directory: str,
        include_negative: bool = False,
        include_in: bool = False,
        precision: int = 6) -> bool:
    """
    Processes enrichment data files in the specified directory and generates CSV output files
    in a 'pivoted' form, where each file contains the values for all the rounds for that sequence
    and metric/measure.

    This function reads CSV files from the specified directory, processes them to include or exclude
    certain columns based on the `include_negative` parameter, merges the data, and writes the final
    sorted output to new CSV files. The CSV files are expected to have the actual data starting from
    the 7th row, and the column headers are on the 7th row.

    Parameters:
    directory (str): The directory containing the CSV files to be processed.
    include_negative (bool): A flag indicating whether to include files for the 'negative' 
                             frequencies and enrichments.
                             If True, files are output for the negative enrichment, the ratio,
                             the out enrichment, and the frequence for negative and out files.
                             If False, only the 'post' files are included. Default is False.
                             This will be True if ANY round has a negative control file.
    include_in (bool): A flag indicating whether to include files for the 'pre' frequencies.
                       If True, all_rounds_frequency_in_results.csv will be created,
                       otherwise it will not. include_in should be True if ANY of the rounds
                       have an actual 'pre' file and will be False if NONE of the rounds have
                       an 'pre' file.
    precision (int): The number of decimal places to use for floating point 
                     numbers in the output CSV files.
                     Default is 6.

    Returns:
    bool: True if the processing is completed successfully.

    Notes:
    - The function expects the files in the directory to have names
      in a specific format where parts of the filename are separated
      by underscores ('_'), and it uses the second part of the filename as a prefix
      for the columns.
    - The function ignores hidden files (those starting with a dot).
    - The merged DataFrame is sorted by the last column in descending order
        before being written to the output files.

    Example:
    ```
    dir_path = 'path/to/your/directory'
    result = write_enrichments_final_output(dir_path, include_negative=True, precision=6)
    if result:
        print("Enrichment data processed and output files created successfully.")
    ```

    """
    files = [file for file in os.listdir(directory) if not file.startswith('.')]
    merged_df = None
    columns_to_keep = ['Unique_Sequence_Name', 'Sequence', 'Enr_post', 'Freq_post']
    if include_negative is True:
        columns_to_keep.extend(['Enr_ratio', 'Enr_neg', 'Freq_neg'])
    if include_in is True:
        columns_to_keep.extend(['Freq_pre'])

    for i, file in enumerate(files):
        rnd = file.split('_')[1]
        with open(f"{directory}/{file}", 'r', encoding='utf-8', errors='replace') as f:
            df_temp = pd.read_csv(f, skiprows = 6)
        df_temp = df_temp[columns_to_keep]
        df1_prefixed = df_temp.rename(
            columns =
                lambda x, rnd = rnd:
                    f"{rnd}_{x}" if x not in ['Unique_Sequence_Name', 'Sequence'] else x
            )
        if i == 0:
            merged_df = df1_prefixed
        else:
            merged_df = pd.merge(
                merged_df,
                df1_prefixed,
                on=['Unique_Sequence_Name','Sequence'],
                how='outer'
            )
    for col in columns_to_keep:
        if col in ['Unique_Sequence_Name','Sequence']:
            continue
        final_cols_to_keep = ['Unique_Sequence_Name','Sequence']
        temp_cols = []
        for coln in merged_df.columns:
            if coln.endswith(col):
                temp_cols.append(coln)
        final_cols_to_keep.extend(sorted(temp_cols))
        expand_name = col.lower().replace(
            'enr','enrichment').replace('neg','negative').replace('freq','frequency')
        file_name = f"all_rounds_{expand_name}_results.csv"
        final_output = merged_df[final_cols_to_keep]
        final_output_sorted = final_output.sort_values(by=final_output.columns[-1], ascending=False)
        for coln in final_output.columns:
            if coln.lower().startswith('freq'):
                final_output[coln] = final_output[coln].apply(lambda x: f"{x:.{precision}f}%")

        final_output_sorted.to_csv(
            f"{directory}/{file_name}",
            index = False,
            header = True,
            float_format=f"%.{precision}f"
        )
    return True

def find_enrichments(output_dir: str, precision_input: int = 6) -> bool:
    """
    Main function to find enrichments in modified counts data.

    This function runs the modified counts script 
    for multiple rounds, processing the counts data, merging it,
    and writing the enriched results to an output directory. 
    Progress is printed at each step.
    """
    # Parse command-line arguments
    print("enrichment_analysis <=> "+
          "Processing enrichments for the 'counts' and 'counts_aa' output folders")

    precision_input = 6 if precision_input is None else precision_input

    # read the enrichment_analysis_file_sorting_logic.csv file
    rounds_data = pd.read_csv(f"{output_dir}/enrichment_analysis_file_sorting_logic.csv")

    # Set directory path
    for ind, counts_type in enumerate(
        tqdm(['counts','counts_aa'], desc = 'Processing each counts output folder')
        ):
        counts_dir = os.path.join(output_dir, counts_type)
        if not os.path.isdir(counts_dir):
            continue

        if check_rounds_file(rounds_data, counts_dir) is False:
            print('data in enrichment_analysis_file_sorting_logic.csv file incorrect '+
                f'does not match the files found in the directory: {counts_dir}'
            )
            continue

        # Get the maximum round
        max_round = rounds_data['round_number'].max()

        # Check if there are any negative controls
        neg_files_exist = any(rounds_data['file_type'] == 'negative')
        pre_files_exist = any(rounds_data['file_type'] == 'pre')
        for i in tqdm(
            range(1, max_round + 1),
            desc = f"Processing each round for the {counts_type} enrichment analysis", leave = False
            ):
            post_file = get_first_matching_file(counts_dir, rounds_data, 'post', i)
            neg_file = get_first_matching_file(counts_dir, rounds_data, 'negative', i)
            pre_file = get_first_matching_file(counts_dir, rounds_data, 'pre', i)
            if pre_file is None and i > 1:
                pre_file = get_first_matching_file(counts_dir, rounds_data, 'post', i-1)

            merged_data = merge_data_for_rounds(
                post_df = easy_diver_counts_to_df(
                    post_file, i, 'post'),
                pre_df = easy_diver_counts_to_df(
                    pre_file, i, 'pre'),
                neg_df = easy_diver_counts_to_df(
                    neg_file, i, 'neg')
            )

            enrich_and_write(
                merged_data,
                f"{output_dir}/modified_{counts_type}/round_{str(i).zfill(3)}_enrichment_analysis",
                precision_input,
                include_negative = neg_files_exist
            )

            # Calculate & print progress
            print(f"(Approx.) Progress: {i * 100 / max_round / (2 - ind)} %")

        write_enrichments_final_output(
            f"{output_dir}/modified_{counts_type}",
            neg_files_exist,
            pre_files_exist,
            precision_input
        )
    return True
