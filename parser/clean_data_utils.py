import pandas as pd
import numpy as np

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
