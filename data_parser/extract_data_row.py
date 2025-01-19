import pdfplumber
import pandas as pd
import numpy as np


DEFAULT_EXTRACTION_SETTINGS = {
    "vertical_strategy": "text",    
    "horizontal_strategy": "lines", 
    "intersection_tolerance": 20, 
    "snap_tolerance" : 1
}




def extract_table_from_pdf(pdf_path, settings = DEFAULT_EXTRACTION_SETTINGS):
    data = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # Extract table(s) from the current page. 
            # You may need to adjust table settings depending on the PDF layout.
            tables = page.extract_tables(table_settings=settings)
            for table in tables:
                for row in table:
                    #print(row)
                    data.append(row)
            
            
            
    return data

def merge_split_rows(table_rows):
    """
    Merges rows that appear to be broken-up parts of a single logical row.
    If a row has only one non-empty element, merge that content into the previous row
    and do not add the current row to the output dataset.
    This version handles NoneType cells.
    """
    merged_rows = []
    for row in table_rows:
        # Replace None with an empty string
        
        row = [cell if cell is not None else "" for cell in row]
        
        # Count non-empty cells (after stripping whitespace)
        non_empty_cells = [cell for cell in row if cell.strip()]
        
        # If the row appears to be a continuation (only one non-empty cell)
        # and there's already a previous row, merge its content and DO NOT append this row.
        if len(non_empty_cells) == 1 and merged_rows:
            for i, cell in enumerate(row):
                if cell.strip():
                    prev_cell = merged_rows[-1][i].strip()
                    merged_rows[-1][i] = (prev_cell + " " if prev_cell else "") + cell.strip()
            # Skip appending this row entirely.
        elif len(non_empty_cells) > 0:
            # Otherwise, clean up the row (strip each cell) and append as a new row.
            cleaned_row = [cell.strip() for cell in row]
            merged_rows.append(cleaned_row)
    return merged_rows


def remove_empty_columns(table_rows, empty_threshold=0.9):
    """
    Removes columns that are empty in at least `empty_threshold` fraction of rows.
    Handles rows with varying lengths by first padding shorter rows with empty strings.
    """
    # Determine maximum row length
    max_length = max(len(row) for row in table_rows)
    
    # Pad rows that are shorter than max_length
    padded_rows = [row + [""] * (max_length - len(row)) for row in table_rows]
    
    # Convert to numpy array for easier column-wise operations
    arr = np.array(padded_rows, dtype=object)
    n_rows = arr.shape[0]
    
    # Determine which columns to keep
    columns_to_keep = []
    for col in range(arr.shape[1]):
        # Count empty cells after stripping whitespace in this column
        empty_count = sum(1 for cell in arr[:, col] if not (cell and cell.strip()))
        # If the fraction of empty cells is below the empty_threshold, keep the column
        if empty_count / n_rows < empty_threshold:
            columns_to_keep.append(col)
    
    # Reconstruct the table using only the columns to keep
    cleaned_table = [[row[col] for col in columns_to_keep] for row in padded_rows]
    return cleaned_table

# ----- Example usage -----
def fix_transaction_description(rows):
    """
    Processes extracted rows by:
      1. Scanning for any entry in column 2 (index 1) with more than 2 newline characters.
      2. Checking how many following rows have a None/empty entry in column 2,
         storing that number in 'num_transactions_to_fix'.
      3. Splitting the long text into groups such that:
           - The first group remains in the row with the extended text.
           - Each group stops immediately after the second newline is encountered.
      4. Inserting the first 'num_transactions_to_fix' text groups into the subsequent rows by updating column 2.
      
    The function assumes each row is a list and that column 2 is at index 1.
    
    Returns a new list of rows with the fixed descriptions.
    """
    fixed_rows = list(rows)  # shallow copy is enough if inner lists are replaced
    num_rows = len(fixed_rows)
    i = 0
    while i < num_rows:
        # Normalize the entry in column 2 for the current row.
        cell = fixed_rows[i][1] if fixed_rows[i][1] is not None else ""
        cell = cell.strip()
        # Check if there are more than 2 newline characters.
        if cell.count("\n") > 2:
            # Count how many following rows have an empty entry in column 2.
            num_transactions_to_fix = 0
            j = i + 1
            while j < num_rows and (fixed_rows[j][1] is None or fixed_rows[j][1].strip() == ""):
                num_transactions_to_fix += 1
                j += 1

            # Split the long text from cell into groups.
            # We will iterate over the characters and break as soon as we see the second newline.
            groups = []
            current_group = ""
            newline_count = 0
            for ch in cell:
                current_group += ch
                if ch == "\n":
                    newline_count += 1
                    if newline_count == 2:
                        groups.append(current_group)
                        current_group = ""
                        newline_count = 0
            # Append any remaining text as the final group (if not empty).
            if current_group:
                groups.append(current_group)

            # Keep the first grouping in the original row.
            # Then, assign the next groupings (up to num_transactions_to_fix) to the subsequent rows.
            if groups:
                fixed_rows[i][1] = groups[0]
                for k in range(1, min(num_transactions_to_fix + 1, len(groups))):
                    fix_row_index = i + k
                    fixed_rows[fix_row_index][1] = groups[k]
            # If there are more groups than rows to fix, you can decide whether to merge them
            # into the original row (after a separator) or ignore them.
            
            # Skip ahead past the rows we just processed.
            i = j
        else:
            i += 1
    return fixed_rows

