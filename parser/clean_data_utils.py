import pandas as pd
import numpy as np
import warnings
from dateutil import parser


def merge_dollar_cr_cells(rows):
    """
    For each row, checks each cell for the '$' character.
    If a cell contains '$' and the cell immediately to the right contains 'CR',
    merges the two cells into the right cell and replaces the cell with '$' with an empty string.
    """
    updated_rows = []
    for row in rows:
        # Work on a mutable copy of the row
        new_row = row.copy()
        # Iterate over indices from 0 to second-to-last cell
        for i in range(len(new_row) - 1):
            cell = new_row[i]
            right_cell = new_row[i + 1]
            if "$" in cell and "CR" in right_cell:
                # Split the cell by the first occurrence of '$'
                left_part, right_part = cell.split("$", 1)
                # Prepend the '$' to the right_part so that we get the full substring.
                dollar_substring = "$" + right_part
                # Merge with the right cell.
                new_row[i + 1] = f"{dollar_substring}{right_cell}".strip()
                # Replace the original cell with the left part if it exists or an empty string.
                new_row[i] = left_part.strip() if left_part.strip() else ""
        updated_rows.append(new_row)
    return updated_rows

def clean_cell_dollar_cr(dataset):
    """
    Applies the clean_cell function to every cell in the dataset.
    
    Parameters:
      dataset (list of list of str): The input data where each row is a list of cells.
      
    Returns:
      list of list of str: A new dataset with all cells cleaned.
    """
    def clean_cell(cell):
        if cell is None or not isinstance(cell, str):
            return ""
        cleaned = cell.replace("$", "").replace("CR", "")
        return cleaned.strip()
    
    cleaned_dataset = []
    for row in dataset:
        cleaned_row = [clean_cell(cell) for cell in row]
        cleaned_dataset.append(cleaned_row)
    return cleaned_dataset


def is_date(string, fuzzy=True):
    """
    Tries to parse a string as a date.
    Returns the parsed date if successful, otherwise returns None.
    """
    try:
        # parser.parse returns a datetime, but you can choose to format it as needed.
        with warnings.catch_warnings():
            warnings.simplefilter("error")  # treat all warnings as errors
            return parser.parse(string, fuzzy=fuzzy)
            
        
    except (ValueError, TypeError, OverflowError, Exception):
        return None

def create_dataset(processed_data):
    """
    Given a processed dataset (list of lists), creates an empty DataFrame with the same number
    of rows and columns 'Date', 'Transaction Description', 'Debit', 'Credit', 'Balance'.
    It then scans each row for the first date (from left to right) and places it in the 'Date' column.
    If no date is found, None is placed.
    
    Parameters:
      processed_data (list of list): The processed dataset.
      
    Returns:
      pd.DataFrame: DataFrame with the new columns, where the 'Date' column is populated.
    """
    num_rows = len(processed_data)
    # Create an empty DataFrame with the desired columns.
    df = pd.DataFrame({
        "Date": [None] * num_rows,
        "Transaction Description": [None] * num_rows,
        "Debit": [None] * num_rows,
        "Credit": [None] * num_rows,
        "Balance": [None] * num_rows
    })
    
    # For each row in the processed dataset, scan for a date string.
    def extract_numeric(cell):
        try:
            return float(cell.replace(",", "").strip())
        except (ValueError, AttributeError):
            return None

    # Process each row
    for idx, row in enumerate(processed_data):
        found_date = None
        numeric_values = []
        
        # Scan for a date and numeric values in the row
        for cell in row:
            if cell is not None and isinstance(cell, str):
                if "." not in cell:  # Skip cells with "."
                    parsed_date = is_date(cell, fuzzy=False)
                    if parsed_date is not None and found_date is None:
                        found_date = parsed_date
                # Try to extract numeric values from the cell
                num = extract_numeric(cell)
                if num is not None:
                    numeric_values.append(num)

        # Assign the first found date (if any)
        df.at[idx, "Date"] = found_date

        # Assign the balance and determine debit/credit
        if numeric_values:
            # Rightmost numeric value is the balance
            balance = numeric_values[-1]
            df.at[idx, "Balance"] = balance
            
            # Second rightmost numeric value is used for debit/credit
            if len(numeric_values) > 1:
                second_last = numeric_values[-2]
                # Determine whether it's debit or credit
                if idx > 0:
                    prev_balance = df.at[idx - 1, "Balance"]
                    if prev_balance is not None and balance < prev_balance:
                        if second_last is not None:
                            df.at[idx, "Debit"] = second_last
                        else:
                            df.at[idx, "Debit"] = prev_balance-balance
                    elif prev_balance is not None:
                        if second_last is not None:
                            df.at[idx, "Credit"] = second_last
                        else:
                            df.at[idx, "Debit"] = -prev_balance+balance
                else:
                    # For the first row, assume it's a credit
                    df.at[idx, "Credit"] = second_last
        else:
            # If no numeric values, leave Balance, Debit, and Credit as None
            df.at[idx, "Balance"] = None
            df.at[idx, "Debit"] = None
            df.at[idx, "Credit"] = None

    return df

