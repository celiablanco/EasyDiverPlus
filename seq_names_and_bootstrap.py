#!/usr/bin/python

import os
import json
import argparse
from concurrent.futures import ProcessPoolExecutor
from typing import Optional, List, Callable, Any, Tuple
import pandas as pd
import numpy as np

def base_encode(sequence_number: int, prefix: str) -> str:
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
        return f"{prefix}_"+chars58[0]
    encoded = []
    while sequence_number > 0:
        sequence_number, rem = divmod(sequence_number, len(chars58))
        encoded.insert(0, chars58[rem])
    return f"{prefix}_"+"".join(encoded)

def unique_sequence_name_generator(row: pd.Series, sequence_dict: dict, prefix: str) -> str:
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
    
    encoded_name = base_encode(len(sequence_dict) + 1, prefix)
    sequence_dict[row['Sequence']] = encoded_name
    return encoded_name

def bootstrap_counts_binomial(
        total_counts: int,
        count_seq: int,
        sequence: str,
        count_seq_dict: dict,
        bootstrap_depth: int = 1000,
        seed: int = 42
    ) -> tuple[str, List[float]]:
    """
    Performs bootstrap binomial sampling on counts data.

    Parameters:
    total_counts (int): Total number of counts.
    count_seq (int): Number of sequences.
    sequence (str): Sequence identifier.
    count_seq_dict: Bootstrapping dictionary to hold boostrap data
    bootstrap_depth (int): Number of bootstrap samples to generate. Default is 1000.
    seed (int): Random seed for reproducibility. Default is 42.

    Returns:
    tuple: A tuple containing the sequence identifier 
        and the 95% confidence interval of the bootstrapped counts as [lower, upper].
    """
    if seed is not None:
        np.random.seed(seed)
    if count_seq_dict.get(count_seq) is not None:
        return sequence, count_seq_dict.get(count_seq).get('bootstrap')
    else:
        bootstrapped_counts = np.random.binomial(
            total_counts, count_seq / total_counts, size = bootstrap_depth
        )
        # Calculate the 95% confidence interval
        bootstrapped_95_confidence_interval = [
            np.percentile(bootstrapped_counts, 2.5),
            np.percentile(bootstrapped_counts, 97.5)
        ]
        count_seq_dict[count_seq]['bootstrap'] = list(np.around(np.array(bootstrapped_95_confidence_interval), 2))
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
    total_counts, row, count_column, sequence_column, bootstrap_dict, bootstrap_depth, func = args
    count_seq = row[count_column]
    sequence = row[sequence_column]
    return func(total_counts, count_seq, sequence, bootstrap_dict, bootstrap_depth)

def parallel_apply(
        df: pd.DataFrame,
        func: Callable[[int, int, str, int], Any],
        count_column: str,
        sequence_column: str,
        total_counts: int,
        bootstrap_dict: dict,
        bootstrap_depth: int) -> List[Any]:
    # Prepare arguments for each row
    args_list = [(total_counts, row, count_column, sequence_column, bootstrap_dict, bootstrap_depth, func) for _, row in df.iterrows()]

    # Use ProcessPoolExecutor for parallel processing
    with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        results = list(executor.map(process_row, args_list))

    return results

def easy_diver_counts_to_df(filename: str, bootstrap_dict: dict) -> pd.DataFrame:
    """
    Converts an Easy Diver counts file to a pandas DataFrame, 
    including bootstrapped confidence intervals.

    Parameters:
    filename (str): The path to the counts file.
    bootstrap_dict (dict): The bootstrap results holder dictionary

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
    df['Freq'] = 100 * (df['Count']/total_mols)
    df['Freq'] = df['Freq'].apply(lambda x: f"{x:.10f}%")
    df['Total_Unique_Sequences'] = num_seqs
    df['Total_Molecules'] = total_mols
    
    results = parallel_apply(df, bootstrap_counts_binomial, 'Count', 'Sequence', total_mols, bootstrap_dict, 1000)
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
    df['Count_Upper'] = df['Count_Upper'].astype(int)
    df['Count_Lower'] = df['Count_Lower'].astype(int)

    df['Freq_Lower'] = 100 * (df['Count_Lower']/df['Total_Molecules'])
    df['Freq_Upper'] = 100 * (df['Count_Upper']/df['Total_Molecules'])

    df['Freq_Lower'] = df['Freq_Lower'].apply(lambda x: f"{x:.10f}%")
    df['Freq_Upper'] = df['Freq_Upper'].apply(lambda x: f"{x:.10f}%")

    return num_seqs, total_mols, df

def write_output_file(file: str, df: pd.DataFrame, unique_sequences: int, total_molecules: int) -> str:
    # Determine the maximum length of the string representation of each column's data
    temp_filename = file.replace(".txt", "") + 'temp.csv'
    filename = file.replace(".txt", "") + '.csv'
    try:
        df.to_csv(
                temp_filename,
                index = False,
                header = True
            )
        extra_header = f"""number of unique sequences,{unique_sequences}
total number of molecules,{total_molecules}"""
        original_content = ""
        with open(temp_filename, 'r', encoding='utf-8') as original_file:
            original_content = original_file.read()

        # Write the new block of text and the original content to a new file
        with open(filename, 'w', encoding='utf-8') as new_file:
            new_file.write(extra_header + '\n\n' + original_content)
    except (OSError, IOError) as e:
        print(f"Failed writing the {filename} file. Exception encountered: {e}")
        return ""
    try:
        # Remove the original CSV file
        os.remove(temp_filename)
    except (OSError, IOError) as e:
        print(f"Failed to remove the temporary file {temp_filename} for the {filename} results file process. "+
              f"Exception encountered: {e}"
        )
        return ""

    return filename

def main():
    # Create the parser
    parser = argparse.ArgumentParser(description="Process counts (or counts.aa) files to add bootstrapping and unique sequence name.")
    # Add the -dir flag (required argument)
    parser.add_argument(
        '-file',
        type=str,
        required=True,
        help='The file path for the counts file to alter.'
    )

    parser.add_argument(
        '-seqdict',
        type=str,
        required=True,
        help='The file path for the sequence dictionary.'
    )

    parser.add_argument(
        '-bootdict',
        type=str,
        required=True,
        help='The file path for the boostrapping dictionary.'
    )

    # Parse the arguments
    args = parser.parse_args()
    
    file_path = args.file
    seq_dict_path = args.seqdict
    boot_dict_path = args.bootdict
    print(f'working on file {file_path}...converting the .txt file to .csv and ' +
          'adding in unique sequence name')
    prefix = 'nt'
    if ".aa" in file_path:
        prefix = 'aa'

    sequence_dict = {}
    with open(seq_dict_path, "r", encoding='utf-8') as json_file:
        sequence_dict = json.load(json_file)

    bootstrap_dict = {}
    with open(boot_dict_path, "r", encoding='utf-8') as json_file:
        bootstrap_dict = json.load(json_file)

    num_seq, total_mols, counts_df = easy_diver_counts_to_df(file_path, bootstrap_dict)

    counts_df['Unique_Sequence_Name'] = counts_df.apply(
        unique_sequence_name_generator,
        axis = 1,
        sequence_dict = sequence_dict,
        prefix = prefix
    )
    final_columns = ['Unique_Sequence_Name','Sequence','Count','Count_Lower','Count_Upper','Freq','Freq_Lower','Freq_Upper']
    print('writing new output file')
    output_filename = write_output_file(file_path, counts_df[final_columns], num_seq, total_mols)
    print(f'output file written: {output_filename}')

    with open(seq_dict_path, "w", encoding = 'utf-8') as json_file:
        json.dump(sequence_dict, json_file)

    with open(boot_dict_path, "w", encoding = 'utf-8') as json_file:
        json.dump(bootstrap_dict, json_file)

if __name__ == "__main__":
    main()
