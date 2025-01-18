import pdfplumber

def group_words_into_rows(words, y_tolerance=3):
    """
    Groups words (each with x, top, bottom, text, etc.) into rows based on their vertical positions.
    :param words: List of word dictionaries as returned by page.extract_words().
    :param y_tolerance: Maximum difference in y-coordinates to consider words on the same row.
    :return: List of rows; each row is a list of word dictionaries.
    """
    rows = []
    # Sort words by their top coordinate
    words = sorted(words, key=lambda w: w['top'])
    
    for word in words:
        placed = False
        for row in rows:
            # Compare with the first word in the row
            if abs(word['top'] - row[0]['top']) <= y_tolerance:
                row.append(word)
                placed = True
                break
        if not placed:
            rows.append([word])
    return rows

def merge_words_in_row(row, x_gap_threshold=10):
    """
    Merge words in a row into cells. Words with small gaps (less than x_gap_threshold) are 
    merged together; larger gaps denote a cell boundary.
    :param row: List of word dictionaries in a single row.
    :param x_gap_threshold: The gap in x-coordinates that defines a new cell.
    :return: List of strings (each cell's text).
    """
    # Sort words by their x-coordinate
    sorted_row = sorted(row, key=lambda w: w['x0'])
    cells = []
    current_cell = sorted_row[0]['text']
    last_x1 = sorted_row[0]['x1']
    
    for word in sorted_row[1:]:
        # If the gap between the end of the previous word and the start of the current word
        # is small, consider them part of the same cell.
        if word['x0'] - last_x1 < x_gap_threshold:
            current_cell += " " + word['text']
        else:
            cells.append(current_cell.strip())
            current_cell = word['text']
        last_x1 = word['x1']
    cells.append(current_cell.strip())
    return cells

def extract_table_from_layout(pdf_path, y_tolerance=3, x_gap_threshold=5):
    """
    Extracts table-like structure by grouping words based on their positions.
    :param pdf_path: Path to the PDF.
    :param page_number: Which page to process (0-indexed).
    :param y_tolerance: Vertical tolerance for grouping words.
    :param x_gap_threshold: Horizontal gap threshold to determine new cell boundaries.
    :return: List of rows, where each row is a list of cell texts.
    """
    
    all_tables = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # Extract words with bounding box information from the current page.
            words = page.extract_words()
            
            # Group words into rows based on their vertical position.
            row_groups = group_words_into_rows(words, y_tolerance=y_tolerance)
            
            # For each row group, merge words into cells based on horizontal gaps.
            page_table = [merge_words_in_row(row, x_gap_threshold=x_gap_threshold) for row in row_groups]
            all_tables.append(page_table)

    data = []
    for table in all_tables:
        for row in table:
            data.append(row)

    return all_tables
