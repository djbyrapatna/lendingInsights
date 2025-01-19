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


def _is_date(string, fuzzy=True):
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

def _extract_numeric(cell):
    """
    Attempts to extract a numeric value (float) from a cell.
    Returns a float if possible, otherwise returns None.
    """
    try:
        return float(cell.replace(",", "").strip())
    except (ValueError, AttributeError):
        return None


def create_dataset(processed_data):
    """
    Given a processed dataset (list of lists), creates a DataFrame with columns:
      'Date', 'Transaction Description', 'Debit', 'Credit', 'Balance'.
    
    For each row:
      1. If a date is found (scanning left-to-right, ignoring cells containing '.'),
         that date is placed in the 'Date' column.
         Otherwise, the transaction description is all cells from the leftmost onward.
      2. Numeric values in the row are collected; the rightmost numeric value is
         considered the Balance.
      3. If a second rightmost numeric value exists, it is assigned to Debit or Credit,
         based on comparison with the closest previous non-None balance.
      4. The Transaction Description is constructed:
         - If no date was found: concatenate every cell in the row.
         - If a date was found and a balance was found: concatenate the cells 
           between the date cell and the cell containing the debit/credit (if it exists)
           or, if not, between the date cell and the balance cell.
         - If no balance is found, skip the transaction description logic for that row.
      5. Rows with no balance numeric value are later dropped.
    
    Returns:
      A DataFrame with the populated columns.
    """
    num_rows = len(processed_data)
    df = pd.DataFrame({
        "Date": [None] * num_rows,
        "Transaction Description": [None] * num_rows,
        "Debit": [None] * num_rows,
        "Credit": [None] * num_rows,
        "Balance": [None] * num_rows
    })
    
    for idx, row in enumerate(processed_data):
        found_date = None
        date_index = None
        numeric_cells = []  # List of tuples: (index, numeric_value)
        
        # Scan left-to-right for date and numeric values.
        for i, cell in enumerate(row):
            if cell is not None and isinstance(cell, str):
                # When looking for date, ignore cell if it contains a "."
                if "." not in cell and found_date is None:
                    parsed_date = _is_date(cell, fuzzy=False)
                    if parsed_date is not None:
                        found_date = parsed_date
                        date_index = i
                # Attempt to extract numeric value.
                num =_extract_numeric(cell)
                if num is not None:
                    numeric_cells.append((i, num))
        
        # Assign the found date (even if None).
        df.at[idx, "Date"] = found_date
        
        # If no numeric values (and so no balance) are found, skip further processing for this row.
        if not numeric_cells:
            continue
        
        # Balance: the rightmost numeric cell.
        balance_index, balance = numeric_cells[-1]
        df.at[idx, "Balance"] = balance
        
        # Debit/Credit: use second rightmost numeric if available.
        second_numeric = None
        second_index = None
        if len(numeric_cells) > 1:
            second_index, second_numeric = numeric_cells[-2]
            if idx > 0:
                # Search upward for the closest previous non-None balance.
                prev_balance = None
                for search_idx in range(idx - 1, -1, -1):
                    prev_balance = df.at[search_idx, "Balance"]
                    if prev_balance is not None:
                        break
                if prev_balance is not None and balance < prev_balance:
                    df.at[idx, "Debit"] = prev_balance-balance
                elif prev_balance is not None:
                    df.at[idx, "Credit"] = balance-prev_balance
                else:
                    df.at[idx, "Credit"] = second_numeric
            else:
                # For the first row, default to credit.
                df.at[idx, "Credit"] = second_numeric
        else:
            prev_balance = None
            for search_idx in range(idx - 1, -1, -1):
                prev_balance = df.at[search_idx, "Balance"]
                if prev_balance is not None:
                    break
            if prev_balance is not None and balance < prev_balance:
                df.at[idx, "Debit"] = prev_balance-balance
            elif prev_balance is not None:
                df.at[idx, "Credit"] = balance-prev_balance
            
        # Build the Transaction Description.
        description = ""
        # If no date was found, concatenate all cells.
        if found_date is None:
            # If no date was found, but numeric_cells exist, use the rightmost numeric cell index as the endpoint.
            if numeric_cells:
                # Use the rightmost numeric cell index
                end_index = second_index if second_numeric is not None else balance_index
                description = " ".join(cell.strip() for cell in row[:end_index] if cell and isinstance(cell, str))
            else:
                # If no numeric value is found, concatenate everything.
                description = " ".join(cell.strip() for cell in row if cell and isinstance(cell, str))
        else:
            # Only try description logic if we have a found balance.
            if numeric_cells:
                # Determine the endpoint: if second_numeric exists, use its index; otherwise, balance_index.
                end_index = second_index if second_numeric is not None else balance_index
                # Concatenate cells between date_index and end_index (exclusive)
                description_parts = []
                if date_index is not None and date_index < end_index:
                    for cell in row[date_index + 1:end_index]:
                        if cell and isinstance(cell, str) and cell.strip() and not _is_date(cell,fuzzy=False):
                            description_parts.append(cell.strip())
                description = " ".join(description_parts)
        df.at[idx, "Transaction Description"] = description
    
    # Drop any rows with no Balance (i.e. balance remains None).
    df = df[df["Balance"].notnull()].reset_index(drop=True)
    df = df[~df["Transaction Description"].str.contains(r"opening|closing", case=False, na=False)]

    # Drop rows where "Transaction Description" contains "staff assisted" or "cheques written" or "checks written" (case-insensitive)
    df = df[~df["Transaction Description"].str.contains(r"staff assisted|cheques written|checks written", case=False, na=False)]

    #  Drop rows where "Transaction Description" contains only the word "Total" or only the phrase "Account total" (case-insensitive)
    df = df[~df["Transaction Description"].str.strip().str.lower().isin(["total", "account total", "total 0 0 0"])]

    # Build a boolean mask:
    mask_account = df["Transaction Description"].str.contains("account", case=False, na=False)
    mask_keywords = df["Transaction Description"].str.contains("fee|withdrawal|deposit|transfer", case=False, na=False)

    # Drop rows where 'account' is present but none of the keywords are present.
    df = df[~(mask_account & (~mask_keywords))]

    #  Drop any row where the Credit amount is greater than the Balance amount.
    #    (Assuming "Credit" and "Balance" are numeric columns.)
    df = df[~(df["Credit"].notnull() & df["Balance"].notnull() & (df["Credit"] > df["Balance"]))]
    


    return df

