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
import sys
import argparse
import glob
from concurrent.futures import ProcessPoolExecutor
from typing import Optional, List, Callable, Any, Tuple
from tqdm import tqdm
import pandas as pd
import numpy as np

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
        'file_type': ['out', 'in', 'out', 'in'],
        'round_number': [1, 1, 2, 2],
        'filename': ['file1', 'file2', 'file3', 'file4']
    })
    file_type = 'out'
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
    matches = glob.glob(path_pattern+'*.txt')
    return matches[0] if matches else None

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

def base_encode(sequence_number: int) -> str:
    """
    Encodes an integer sequence number into a Base58 string.

    The Base58 encoding uses the characters:
    "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz".
    This excludes characters that can be easily confused, such as '0', 'O', 'I', and 'l'.

    Parameters:
    sequence_number (int): The integer sequence number to encode.

    Returns:
    str: The Base58 encoded string representation of the sequence number.

    Example:
    >>> base_encode(12345)
    '4ER'
    """
    chars58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    if sequence_number == 0:
        return "seq_"+chars58[0]
    encoded = []
    while sequence_number > 0:
        sequence_number, rem = divmod(sequence_number, len(chars58))
        encoded.insert(0, chars58[rem])
    return "seq_"+"".join(encoded)

def unique_sequence_name_generator(row: pd.Series, sequence_dict: dict) -> str:
    """
    Generates a unique sequence name for a given row in a pandas DataFrame.

    If the sequence name already exists in the provided dictionary, it returns the existing name.
    Otherwise, it encodes the row's index into a Base58 string, stores it in the dictionary,
    and returns the new unique sequence name.

    Parameters:
    row (pd.Series): A row from a pandas DataFrame containing the 'Sequence' column.
    sequence_dict (dict): A dictionary mapping sequence names to their unique encoded names.

    Returns:
    str: The unique sequence name for the given row.

    Example:
    >>> import pandas as pd
    >>> df = pd.DataFrame({'Sequence': ['A', 'B', 'A']})
    >>> sequence_dict = {}
    >>> df['UniqueSequenceName'] = df.apply(
            unique_sequence_name_generator, 
            axis=1, 
            sequence_dict=sequence_dict
        )
    >>> df
      Sequence UniqueSequenceName
    0        A                  1
    1        B                  2
    2        A                  1
    """
    if row['Sequence'] in sequence_dict.keys():
        return sequence_dict[row['Sequence']]
    else:
        encoded_name = base_encode(int(row.name))
        sequence_dict[row['Sequence']] = encoded_name
        return encoded_name

def bootstrap_counts_resampling(
        total_counts: int,
        count_seq: int,
        sequence: str,
        bootstrap_depth: int = 1000,
        seed: int = 42
    ) -> tuple[str,List[float]]:
    """
    Performs bootstrap resampling on counts data. 
    Can be used instead of 'binomial' approach.
    Binomial approach is currently used for this script, 
    but leaving this here for potential use in future.

    Parameters:
    total_counts (int): Total number of counts.
    count_seq (int): Number of sequences.
    sequence (str): Sequence identifier.
    bootstrap_depth (int): Number of bootstrap samples to generate. Default is 1000.
    seed (int): Random seed for reproducibility. Default is 42.

    Returns:
    tuple: A tuple containing the sequence identifier 
        and the 95% confidence interval of the bootstrapped counts as [lower, upper].
    """
    if seed is not None:
        np.random.seed(seed)
    # Sample with 1 representing seq A and 0 representing other seqs
    sample = np.array(
        [1 for _ in range(count_seq)] + [0 for _ in range(total_counts - count_seq)]
    )
    bootstrapped_counts = [
        np.sum(
            np.random.choice(sample, size=len(sample), replace=True)
        ) for _ in range(bootstrap_depth)
    ]
    # Some related statistics
    # bootstrapped_mean = np.mean(bootstrapped_counts)
    # bootstrapped_sd = np.std(bootstrapped_counts, ddof=1)
    # bootstrapped_median = np.percentile(bootstrapped_counts, 50)
    bootstrapped_95_confidence_interval = [
        np.percentile(bootstrapped_counts, 2.5),
        np.percentile(bootstrapped_counts, 97.5)
    ]

    return sequence, list(np.around(np.array(bootstrapped_95_confidence_interval),2))

def bootstrap_counts_binomial(
        total_counts: int,
        count_seq: int,
        sequence: str,
        bootstrap_depth: int = 1000,
        seed: int = 42
    ) -> tuple[str,List[float]]:
    """
    Performs bootstrap binomial sampling on counts data.

    Parameters:
    total_counts (int): Total number of counts.
    count_seq (int): Number of sequences.
    sequence (str): Sequence identifier.
    bootstrap_depth (int): Number of bootstrap samples to generate. Default is 1000.
    seed (int): Random seed for reproducibility. Default is 42.

    Returns:
    tuple: A tuple containing the sequence identifier 
        and the 95% confidence interval of the bootstrapped counts as [lower, upper].
    """
    if seed is not None:
        np.random.seed(seed)
    bootstrapped_counts = np.random.binomial(
        total_counts, count_seq / total_counts, size = bootstrap_depth
    )
    # Calculate the 95% confidence interval
    bootstrapped_95_confidence_interval = [
        np.percentile(bootstrapped_counts, 2.5),
        np.percentile(bootstrapped_counts, 97.5)
    ]
    return sequence, list(np.around(np.array(bootstrapped_95_confidence_interval), 2))

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
    num_unique_sequences = int(lines[0].split('=')[1].strip())
    total_num_molecules = int(lines[1].split('=')[1].strip())

    return num_unique_sequences, total_num_molecules

def process_row(args: Tuple[int, pd.Series, str, str, int, Callable]) -> Tuple[str, List[float]]:
    total_counts, row, count_column, sequence_column, bootstrap_depth, func = args
    count_seq = row[count_column]
    sequence = row[sequence_column]
    return func(total_counts, count_seq, sequence, bootstrap_depth)

def parallel_apply(
        df: pd.DataFrame,
        func: Callable[[int, int, str, int], Any],
        count_column: str,
        sequence_column: str,
        total_counts: int,
        bootstrap_depth: int) -> List[Any]:
    # Prepare arguments for each row
    args_list = [(total_counts, row, count_column, sequence_column, bootstrap_depth, func) for _, row in df.iterrows()]

    # Use ProcessPoolExecutor for parallel processing
    with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        results = list(executor.map(process_row, args_list))

    return results

def easy_diver_counts_to_df(filename: str, ed_round: int, ftype: str) -> pd.DataFrame:
    """
    Converts an Easy Diver counts file to a pandas DataFrame, 
    including bootstrapped confidence intervals.

    Parameters:
    filename (str): The path to the counts file.
    ed_round (int): The round number.
    ftype (str): The type of the file (e.g., 'out', 'in', 'neg').

    Returns:
    pd.DataFrame: The DataFrame with the counts and calculated confidence intervals.
    """
    if filename is None:
        return None

    num_seqs, total_mols = easy_diver_parse_file_header(filename)
    df = pd.read_csv(
        filename,
        sep=r'\s+',
        skiprows=3,
        header=None
    )

    df.columns = ['Sequence', 'Count', 'Freq']
    df['Count'] = df['Count'].astype(int)
    df['Freq'] = df['Count']/total_mols
    df['Total_Unique_Sequences'] = num_seqs
    df['Total_Molecules'] = total_mols
    df['Round'] = ed_round
    df['Type'] = ftype
    
    results = parallel_apply(df, bootstrap_counts_binomial, 'Count', 'Sequence', total_mols, 1000)
    results_df = pd.DataFrame(
        results,
        columns = ['Sequence','Bootstrapped_95CI']
    )
    results_df[['Count_Lower', 'Count_Upper']] = pd.DataFrame(
        results_df['Bootstrapped_95CI'].tolist(),
        index = results_df.index
    )
    df = pd.merge(
        df,
        results_df[['Sequence', 'Count_Lower', 'Count_Upper']],
        on='Sequence',
        how='inner'
    )

    df['Count_Lower'] = df['Count_Lower'].replace(0, 1)

    df['Freq_Lower'] = df['Count_Lower']/df['Total_Molecules']
    df['Freq_Upper'] = df['Count_Upper']/df['Total_Molecules']

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
    if row['Freq_Lower_in'] > 0:
        # If the max is more than 1, we've set the min to more than 1

        # Min enrichment due to selection - assumes smallest f_out and largest f_in
        enr_post_min = safe_divide(row['Freq_Lower_out'], row['Freq_Upper_in'])

        # Max enrichment due to selection - assumes largest f_out and smallest f_in
        enr_post_max = safe_divide(row['Freq_Upper_out'], row['Freq_Lower_in'])

        if include_negative:
            enr_neg_min = safe_divide(row['Freq_Lower_neg'], row['Freq_Upper_in'])
            enr_neg_max = safe_divide(row['Freq_Upper_neg'], row['Freq_Lower_in'])
        else:
            enr_neg_min = None
            enr_neg_max = None
    else:  # Not enough data to make an estimate
        enr_post_min = 0
        enr_post_max = 0
        enr_neg_min = 0
        enr_neg_max = 0

    if enr_post_max > 0:  # Makes sense to print enr_post
        enr_post = safe_divide(row['Freq_out'], row['Freq_in'])
    else:
        enr_post = None

    if include_negative and enr_neg_max > 0:  # 2A, 2B case check
        enr_neg = safe_divide(row['Freq_neg'], row['Freq_in'])
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
        'Enr_out': enr_post,
        'Enr_out_lower': None if enr_post is None else enr_post_min,
        'Enr_out_upper': None if enr_post is None else enr_post_max,
        'Enr_neg': enr_neg,
        'Enr_neg_lower': None if enr_neg is None else enr_neg_min,
        'Enr_neg_upper': None if enr_neg is None else enr_neg_max,
        'Enr_ratio': safe_divide(enr_post, enr_neg),
        'Enr_ratio_lower': enr_ratio_min,
        'Enr_ratio_upper': enr_ratio_max
    }

def merge_data_for_rounds(
        out_df: pd.DataFrame,
        sequence_dict: dict,
        in_df: Optional[pd.DataFrame] = None,
        neg_df: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
    """
    Merges data from different files for the 
    same round into a single DataFrame.

    Parameters:
    out_df (pd.DataFrame): The primary DataFrame, sourced from the 'out' file.
    sequence_dict (dict): The global dictionary used to hold all the unique sequence names.
    in_df (Optional[pd.DataFrame]): The secondary DataFrame to merge, 
        sourced from the 'in' file. Default is None.
    neg_df (Optional[pd.DataFrame]): The tertiary DataFrame to merge,
        sourced from the 'neg' file. Default is None.
    
    Returns:
    pd.DataFrame: The merged DataFrame, 
        sorted by the `out` count column, `Count_out` in descending order.
    """
    # Merge the first two DataFrames on 'Sequence' with a full join
    columns_to_keep = [
        'Sequence', 'Count', 'Count_Lower', 'Count_Upper',
        'Freq', 'Freq_Lower', 'Freq_Upper',
        'Total_Unique_Sequences', 'Total_Molecules'
    ]

    if in_df is not None:
        merged_df = pd.merge(
            out_df[columns_to_keep],
            in_df[columns_to_keep],
            on='Sequence',
            how='left',
            suffixes=(f"_{out_df['Type'][0]}", f"_{in_df['Type'][0]}")
        )
    elif neg_df is not None:
        merged_df = pd.merge(
            out_df[columns_to_keep],
            neg_df[columns_to_keep],
            on='Sequence',
            how='left',
            suffixes=(f"_{out_df['Type'][0]}", f"_{neg_df['Type'][0]}")
        )
    # If a third DataFrame is provided, merge it as well with a full join
    if neg_df is not None and in_df is not None:
        merged_df = pd.merge(
            merged_df,
            neg_df[columns_to_keep],
            on='Sequence',
            how='left',
            suffixes=('', f"_{neg_df['Type'][0]}")
        )
        # ensure the remaining columns have '_neg' suffix
        merged_df.columns = [
            col+'_neg'
            if col != 'Sequence' and col in out_df.columns
            else col
            for col in merged_df.columns
        ]
    else:
        merged_df = out_df[columns_to_keep]
        # ensure the columns of the single df have '_out' suffix
        merged_df.columns = [
            col+'_out' if col != 'Sequence' and col in out_df.columns
            else col
            for col in merged_df.columns
        ]

    sorted_df = merged_df.sort_values(by = 'Count_out', ascending = False)
    sorted_df['Unique_Sequence_Name'] = sorted_df.apply(
        unique_sequence_name_generator,
        axis=1,
        sequence_dict=sequence_dict
    )

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
    for group in ['neg','in']:
        if f"Count_{group}" not in sorted_df.columns:
            for col in [
                'Count', 'Count_Lower', 'Count_Upper',
                'Freq', 'Freq_Lower', 'Freq_Upper',
                'Total_Unique_Sequences' , 'Total_Molecules'
            ]:
                sorted_df[f"{col}_{group}"] = np.nan

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
            'Count_in','Count_Lower_in','Count_Upper_in',
            'Freq_in','Freq_Lower_in','Freq_Upper_in',
            'Count_out','Count_Lower_out','Count_Upper_out',
            'Freq_out','Freq_Lower_out','Freq_Upper_out',
            'Count_neg','Count_Lower_neg','Count_Upper_neg',
            'Freq_neg','Freq_Lower_neg','Freq_Upper_neg',
            'Enr_out','Enr_out_lower','Enr_out_upper',
            'Enr_neg','Enr_neg_lower','Enr_neg_upper',
            'Enr_ratio','Enr_ratio_lower','Enr_ratio_upper'
        ]
    else:
        final_columns = [
            'Unique_Sequence_Name','Sequence',
            'Count_in','Count_Lower_in','Count_Upper_in',
            'Freq_in','Freq_Lower_in','Freq_Upper_in',
            'Count_out','Count_Lower_out','Count_Upper_out',
            'Freq_out','Freq_Lower_out','Freq_Upper_out',
            'Enr_out','Enr_out_lower','Enr_out_upper'
        ]

    enrichments_df = round_df.apply(process_enrichments, axis = 1, result_type = 'expand')
    final_df = pd.merge(round_df, enrichments_df, on = 'Sequence', how = 'inner')
    extras = {}
    for file_type in ['in','out','neg']:
        extras[f"seq_{file_type}"] = int(
                final_df[f"Total_Unique_Sequences_{file_type}"].fillna(0).astype(int)[0]
        )
        extras[f"mol_{file_type}"] = int(
                final_df[f"Total_Molecules_{file_type}"].fillna(0).astype(int)[0]
        )

    extra_header = f"""Number of Unique Sequences (Input),{extras.get('seq_in')}
Total Number of Molecules (Input),{extras.get('mol_in')}
Number of Unique Sequences (Output),{extras.get('seq_out')}
Total Number of Molecules (Output),{extras.get('mol_out')}
Number of Unique Sequences (Neg Control),{extras.get('seq_neg')}
Total Number of Molecules (Neg Control),{extras.get('mol_neg')}"""
    for col in final_df.columns:
        if col.startswith('Count'):
            final_df[col] = final_df[col].fillna(0)
            final_df[col] = final_df[col].astype(int)
        elif col.startswith('Freq'):
            final_df[col] = final_df[col].fillna(0)
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
                             If False, only the 'out' files are included. Default is False.
                             This will be True if ANY round has a negative control file.
    include_in (bool): A flag indicating whether to include files for the 'in' frequencies.
                       If True, all_rounds_frequency_in_results.csv will be created,
                       otherwise it will not. include_in should be True if ANY of the rounds
                       have an actual 'in' file and will be False if NONE of the rounds have
                       an 'in' file.
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
    columns_to_keep = ['Unique_Sequence_Name', 'Sequence', 'Enr_out', 'Freq_out']
    if include_negative is True:
        columns_to_keep.extend(['Enr_ratio', 'Enr_neg', 'Freq_neg'])
    if include_in is True:
        columns_to_keep.extend(['Freq_in'])

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
        expand_name = col.lower().replace('enr','enrichment').replace('neg','negative').replace('freq','frequency')
        file_name = f"all_rounds_{expand_name}_results.csv"
        final_output = merged_df[final_cols_to_keep]
        final_output_sorted = final_output.sort_values(by=final_output.columns[-1], ascending=False)
        final_output_sorted.to_csv(
            f"{directory}/{file_name}",
            index = False,
            header = True,
            float_format=f"%.{precision}f"
        )
    return True

def find_enrichments():
    """
    Main function to find enrichments in modified counts data.

    This function runs the modified counts script 
    for multiple rounds, processing the counts data, merging it,
    and writing the enriched results to an output directory. 
    Progress is printed at each step.
    """
    unique_sequence_dict = {}
    counts_type = ""
    # Parse command-line arguments
    print("SSAILR <=> Processing enrichments for the 'counts' and 'counts.aa' output folders")
    # Create the parser
    parser = argparse.ArgumentParser(description="Process flags for enrichment.")

    # Add the -dir flag (required argument)
    parser.add_argument(
        '-dir',
        type=str,
        required=True,
        help='The directory path.'
    )

    # Add the -precision flag (optional argument)
    parser.add_argument(
        '-precision',
        type=str,
        required=False,
        help='The precision for the decimal numbers. Default is 6'
    )

    # Parse the arguments
    args = parser.parse_args()

    dir_path = args.dir
    precision = 6 if args.precision is None else args.precision

    if dir_path is None:
        print("Directory path not provided.")
        sys.exit(1)

    outdir = dir_path
    # read the enrichment_analysis_file_sorting_logic.csv file
    rounds_data = pd.read_csv(f"{outdir}/enrichment_analysis_file_sorting_logic.csv")

    # Set directory path
    for ind, counts_type in enumerate(
        tqdm(['counts', 'counts.aa'], desc = 'Processing each counts output folder')
        ):
        counts_dir = os.path.join(outdir, counts_type)
        if not os.path.isdir(counts_dir):
            continue

        modified_counts_location = f"modified_{counts_type}"
        files = os.listdir(counts_dir)

        # # Extract round numbers for files matching the criteria
        # round_numbers = [
        #     int(file.split("-out")[0])
        #     for file in files
        #     if "-out" in file and counts_type in file
        # ]

        # Get the maximum round
        max_round = rounds_data['round_number'].max()

        # if rounds_data['round_number'].max() != max_round:
        #     print("number of rounds in sorting map does not match rounds in output")
        #     exit(1)

        # Check if there are any negative controls
        neg_files_exist = any(rounds_data['file_type'] == 'negative')
        in_files_exist = any(rounds_data['file_type'] == 'in')
        for i in tqdm(
            range(1, max_round + 1),
            desc = f"Processing each round for the {counts_type} enrichment analysis", leave = False
            ):
            out_file = get_first_matching_file(counts_dir, rounds_data, 'out', i)
            neg_file = get_first_matching_file(counts_dir, rounds_data, 'negative', i)
            in_file = get_first_matching_file(counts_dir, rounds_data, 'in', i)
            if in_file is None and i > 1:
                in_file = get_first_matching_file(counts_dir, rounds_data, 'out', i-1)

            in_df = easy_diver_counts_to_df(in_file, i, 'in')
            out_df = easy_diver_counts_to_df(out_file, i, 'out')
            neg_df = easy_diver_counts_to_df(neg_file, i, 'neg')

            merged_data = merge_data_for_rounds(
                out_df = out_df, sequence_dict = unique_sequence_dict,
                in_df = in_df, neg_df = neg_df
            )

            enrich_and_write(
                merged_data,
                f"{outdir}/{modified_counts_location}/round_{str(i).zfill(3)}_enrichment_analysis",
                precision,
                include_negative = neg_files_exist
            )

            # Calculate progress
            progress = i * 100 / max_round / (2 - ind)
            print("(Approx.) Progress:", progress, "%")

        write_enrichments_final_output(
            f"{outdir}/{modified_counts_location}",
            neg_files_exist,
            in_files_exist,
            precision
        )

if __name__ == "__main__":
    find_enrichments()
