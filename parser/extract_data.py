import pdfplumber
import pandas as pd
import sys
import numpy as np
import extract_data_row as etr
import clean_data_utils as mr_clean

DEFAULT_EXTRACTION_SETTINGS = {
    "vertical_strategy": "text",    
    "horizontal_strategy": "lines", 
    "intersection_tolerance": 20, 
    "snap_tolerance" : 1
}


def data_extract_and_clean_pipeline(pdf_file, fix_transaction_description=False):
    """
    Runs the entire data extraction and cleaning pipeline:
      1. Extract raw data from the PDF.
      2. Optionally fix transaction descriptions.
      3. Merge split rows.
      4. Remove empty columns.
      5. Merge dollar/CR cells.
      6. Clean all cells for '$' and 'CR'.
      7. Create the final dataset.
      
    Parameters:
      pdf_file (str): Path to the PDF file.
      fix_transaction_description (bool): Whether to fix transaction descriptions.
      
    Returns:
      pd.DataFrame: The final cleaned dataset.
    """
    # Step 1: Extract raw data from PDF.
    raw_data = etr.extract_table_from_pdf(pdf_file)
    
    # Step 2: Optionally fix transaction description issues.
    if fix_transaction_description:
        raw_data = etr.fix_transaction_description(raw_data)
    
    # Step 3: Merge rows that were split.
    merged_rows = etr.merge_split_rows(raw_data)
    
    # Step 4: Remove columns that are mostly empty.
    no_empty_cols = etr.remove_empty_columns(merged_rows, empty_threshold=0.9)
    
    # Step 5: Merge cells where there is a '$' and 'CR' indication.
    balance_merged = mr_clean.merge_dollar_cr_cells(no_empty_cols)
    
    # Step 6: Clean all cells for '$' and 'CR'.
    cleaned_rows = mr_clean.clean_cell_dollar_cr(balance_merged)
    
    # Step 7: Convert the list of cleaned rows into a pandas DataFrame.
    final_dataset = mr_clean.create_dataset(cleaned_rows)
    
    return final_dataset



if __name__ == '__main__':
    arg1 = sys.argv[1]
    if arg1 == "all":
        files = [0,1,3]
        for num in files:
            pdf_file = '../pdfData/Untitled'+str(num)+'.pdf'
            data = data_extract_and_clean_pipeline(pdf_file, fix_transaction_description=(num==3))
            print(data)
    else:
        num = int(sys.argv[1])
        pdf_file = '../pdfData/Untitled'+str(num)+'.pdf'
        data = data_extract_and_clean_pipeline(pdf_file, fix_transaction_description=(num==3))
        for row in data[:50]:
            print (row)
    
    
       
  



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
