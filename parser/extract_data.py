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


def data_extract_and_clean_pipeline(pdf_file, fix_transaction_description = False):
    raw_data = etr.extract_table_from_pdf(pdf_file)
    if fix_transaction_description:
        raw_data= etr.fix_transaction_description(raw_data)
    data_merged = etr.merge_split_rows(raw_data)
    data_merged_and_empty_cols_removed = etr.remove_empty_columns(data_merged, empty_threshold=.9)
    balance_merge_rows = mr_clean.merge_dollar_cr_cells(data_merged_and_empty_cols_removed)
    cleaned_rows = mr_clean.clean_cell_dollar_cr(balance_merge_rows)
    # for row in cleaned_rows[18:28]:
    #     print(row)
    pd1 = mr_clean.create_dataset(cleaned_rows)
    return  pd1






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
