import pdfplumber
import pandas as pd
import sys

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
        else:
            # Clean up extra whitespace in every cell and append the row
            cleaned_row = [cell.strip() for cell in row]
            merged_rows.append(cleaned_row)
    return merged_rows

# Example usage:
# raw_tables = [
#     ['09-May-2018', '09-May-2018', 'ATM-NFS/CASH WITHDRAWAL/+WHITE HOUS', '', '100.00', '', '', '', '9.82'],
#     ['', '', 'E/812912009989', '', '', '', '', '', '']
# ]
# cleaned_tables = merge_split_rows(raw_tables)
# for row in cleaned_tables:
#     print(row)



def debug_pdf(pdf_path, img_path, custom_settings = DEFAULT_EXTRACTION_SETTINGS):
    
    
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        
        # Get a debug image of the page
        debug_img = page.to_image()
        
        # Extract tables using our custom settings
        tables = page.extract_tables(table_settings=custom_settings)
        
        # If tables were extracted, draw boxes around them
        # Note: pdfplumber's extract_tables does not return bounding boxes by default.
        # We can instead use page.find_tables() which returns objects that include bbox info.
        found_tables = page.find_tables(table_settings=custom_settings)
        draw = debug_img.draw
        
        for table in found_tables:
            bbox = table.bbox  # bbox format: (x0, top, x1, bottom)
            # Draw a rectangle around the found table
            draw.rectangle(bbox, outline="red", width=2)
            
        # Save or show the annotated image
        debug_img.save(img_path)
        print("Debug image saved as "+img_path)
        
        # Print the extracted table data for inspection
        if tables:
            for table in tables:
                for row in table:
                    print(row)
        if not tables:
            print("No tables found using the provided settings.")

if __name__ == '__main__':
    num = sys.argv[1]
    pdf_file = '../pdfData/Untitled'+str(num)+'.pdf'
    #debug_pdf(pdf_file, 'debug_page'+str(num)+'.png')
    raw_data = extract_table_from_pdf(pdf_file)
    raw_data_merged = merge_split_rows(raw_data)
    # Optionally, inspect the raw data
    for row in raw_data_merged[:50]:
       print(row)
    pass
