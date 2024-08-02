#!/usr/bin/python

import os
import json
import argparse
from concurrent.futures import ProcessPoolExecutor
from typing import List, Callable, Any, Tuple
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
        bootstrap_dict: dict,
        bootstrap_depth: int = 1000,
        seed: int = 42
    ) -> tuple[str, List[float]]:
    """
    Performs bootstrap binomial sampling on counts data.

    Parameters:
    total_counts (int): Total number of counts.
    count_seq (int): Number of sequences.
    sequence (str): Sequence identifier.
    bootstrap_dict: Bootstrapping dictionary to hold boostrap data
    bootstrap_depth (int): Number of bootstrap samples to generate. Default is 1000.
    seed (int): Random seed for reproducibility. Default is 42.

    Returns:
    tuple: A tuple containing the sequence identifier 
        and the 95% confidence interval of the bootstrapped counts as [lower, upper].
    """
    if seed is not None:
        np.random.seed(seed)

    if bootstrap_dict.get(str(count_seq)) is not None:
        boot = bootstrap_dict.get(str(count_seq)).get('bootstrap')
    else:
        bootstrapped_counts = np.random.binomial(
            total_counts, count_seq / total_counts, size = bootstrap_depth
        )
        # Calculate the 95% confidence interval
        bootstrapped_95_confidence_interval = [
            np.percentile(bootstrapped_counts, 2.5),
            np.percentile(bootstrapped_counts, 97.5)
        ]
        boot = list(np.around(np.array(bootstrapped_95_confidence_interval), 2))
        bootstrap_dict[str(count_seq)] = {
            'bootstrap': boot
        }
    return sequence, boot

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


    # Apply the function directly to each row in the DataFrame
    results = df.apply(
        lambda row: (
            bootstrap_counts_binomial(
                total_mols,
                row['Count'],
                row['Sequence'],
                bootstrap_dict,
                1000
            )  # Bootstrapped_95CI
        ), axis=1
    )
    # Convert the results into a DataFrame
    results_df = pd.DataFrame(results.tolist(), columns=['Sequence', 'Bootstrapped_95CI'])

    # Split the Bootstrapped_95CI into separate columns
    results_df[['Count_Lower', 'Count_Upper']] = pd.DataFrame(
        results_df['Bootstrapped_95CI'].tolist(), index=results_df.index
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

def write_output_file(
        file: str,
        df: pd.DataFrame,
        unique_sequences: int,
        total_molecules: int
    ) -> str:
    """
    Writes the contents of a DataFrame to a CSV file with additional header information.

    This function saves the given DataFrame to a temporary CSV file, reads the content of 
    this temporary file, and then writes it to a new CSV file with additional headers that 
    include the number of unique sequences and the total number of molecules. The temporary 
    file is removed after the new file is successfully created.

    Parameters:
    ----------
    file : str
        The file path (including name) where the final CSV file should be saved. 
        This path should end with ".txt", which will be replaced with ".csv".
    df : pd.DataFrame
        The DataFrame containing the data to be saved.
    unique_sequences : int
        The number of unique sequences to be included in the additional header.
    total_molecules : int
        The total number of molecules to be included in the additional header.

    Returns:
    -------
    str
        The file path of the newly created CSV file with the additional headers.
        Returns an empty string if an error occurs during the file writing process.

    Raises:
    ------
    OSError
        If there is an issue with writing or removing files.
    IOError
        If there is an issue with input/output operations.
    
    Example:
    -------
    >>> df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
    >>> filename = write_output_file("output.txt", df, 2, 10)
    >>> print(filename)
    'output.csv'
    """
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
        print(f"Failed to remove the temporary file {temp_filename} "+
              f"for the {filename} results file process. "+
              f"Exception encountered: {e}"
        )
        return ""

    return filename

def main():
    """
    Main function to process counts files by adding bootstrapping and unique sequence names.

    This function uses argparse to parse command-line arguments, reads the necessary input files 
    (sequence dictionary, bootstrapping dictionary, and counts file), and processes the counts 
    file to add bootstrapping and unique sequence names. It then writes the modified data to a 
    new output file and updates the sequence and bootstrapping dictionaries.

    Command-line Arguments:
    -----------------------
    -file : str
        The file path for the counts file to alter.
    -seqdict : str
        The file path for the sequence dictionary.
    -bootdict : str
        The file path for the bootstrapping dictionary.

    Procedure:
    ----------
    1. Parse the command-line arguments to get the file paths.
    2. Determine the prefix ('nt' or 'aa') based on the counts file extension.
    3. Load the sequence dictionary and bootstrapping dictionary from the specified files.
    4. Convert the counts file to a DataFrame and compute the necessary statistics.
    5. Generate unique sequence names and add them to the DataFrame.
    6. Write the modified data to a new CSV file.
    7. Update and save the sequence and bootstrapping dictionaries.

    Example:
    --------
    $ python script.py -file path/to/counts.txt -seqdict path/to/seqdict.json -bootdict path/to/bootdict.json

    Returns:
    --------
    None
    """
    # Create the parser
    parser = argparse.ArgumentParser(
        description="Process counts (or counts.aa) files "+
        "to add bootstrapping and unique sequence name."
    )
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

    boot_dict = {}
    with open(boot_dict_path, "r", encoding='utf-8') as json_file:
        boot_dict = json.load(json_file)

    num_seq, total_mols, counts_df = easy_diver_counts_to_df(file_path, boot_dict)

    counts_df['Unique_Sequence_Name'] = counts_df.apply(
        unique_sequence_name_generator,
        axis = 1,
        sequence_dict = sequence_dict,
        prefix = prefix
    )
    final_columns = [
        'Unique_Sequence_Name','Sequence',
        'Count','Count_Lower','Count_Upper',
        'Freq','Freq_Lower','Freq_Upper'
    ]
    print('writing new output file')
    output_filename = write_output_file(file_path, counts_df[final_columns], num_seq, total_mols)
    print(f'output file written: {output_filename}')

    with open(seq_dict_path, "w", encoding = 'utf-8') as json_file:
        json.dump(sequence_dict, json_file)

    with open(boot_dict_path, "w", encoding = 'utf-8') as json_file:
        json.dump(boot_dict, json_file)

if __name__ == "__main__":
    main()
