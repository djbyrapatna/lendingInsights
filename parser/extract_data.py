import pdfplumber
import pandas as pd
import sys
import numpy as np
from process_pdf import process_pdf_page_to_pdf
from extract_data_word import extract_table_from_layout

DEFAULT_EXTRACTION_SETTINGS = {
    "vertical_strategy": "text",    
    "horizontal_strategy": "lines", 
    "intersection_tolerance": 20, 
    "snap_tolerance" : 1
}




# Example usage:


if __name__ == '__main__':
    num = sys.argv[1]
    pdf_file = '../pdfData/Untitled'+str(num)+'.pdf'
    #output_pdf = '../pdfData/Untitled'+str(num)+'processed.pdf'
    #process_pdf_page_to_pdf(pdf_path=pdf_file, output_pdf=output_pdf)
    #debug_pdf(pdf_file, 'debug_page'+str(num)+'.png')
    raw_data = extract_table_from_layout(pdf_file, x_gap_threshold=5)
    for row in raw_data[:50]:
        print(row)
    # raw_data = extract_table_from_pdf(pdf_file)
    # data_merged = merge_split_rows(raw_data)
    # data_merged_and_empty_cols_removed = remove_empty_columns(data_merged)
    # # Optionally, inspect the raw data
    # for i, row in enumerate(data_merged_and_empty_cols_removed[:100]):
    #    print(row)
    #    print(data_merged[i])
    



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
