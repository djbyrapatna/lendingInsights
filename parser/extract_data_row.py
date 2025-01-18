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
                    data.append(row)
            
            
            
    return data

def merge_split_rows(table_rows):
    """
    Merges rows that appear to be broken up parts of a single logical row.
    This implementation assumes that if a row has only one non-empty element,
    it likely should be appended to the matching column of the previous row.
    You may need to adjust the logic based on your data's structure.
    """
    merged_rows = []
    for row in table_rows:
        # Replace None with an empty string for processing
        row = [cell if cell is not None else "" for cell in row]
        # Count non-empty cells
        non_empty_cells = [cell for cell in row if cell.strip() != ""]
        if len(non_empty_cells) == 1 and merged_rows:
            # Find the index of the non-empty cell
            for i, cell in enumerate(row):
                if cell.strip() != "":
                    # Append the non-empty cell to the previous row's corresponding cell,
                    # ensuring a space separator if the previous cell isn't empty.
                    prev_content = merged_rows[-1][i].strip()
                    merged_rows[-1][i] = (prev_content + " " if prev_content else "") + cell.strip()
        elif len(non_empty_cells)>0:
            # Clean up extra whitespace in every cell and append the row
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
