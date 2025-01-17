import pdfplumber
import pandas as pd
import sys

def extract_table_from_pdf(pdf_path):
    data = []
    settings = {
        "vertical_strategy": "text",    
        "horizontal_strategy": "text", 
        "intersection_tolerance": 5,    
    }
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # Extract table(s) from the current page. 
            # You may need to adjust table settings depending on the PDF layout.
            tables = page.extract_tables(table_settings=settings)
            for table in tables:
                for row in table:
                    data.append(row)
            words = page.extract_words()
            print(words)
            print('hello')
            for word in words:
                print(word)
    return data

def debug_pdf(pdf_path, img_path):
    custom_settings = {
        "vertical_strategy": "text",    # Try "text" since there are no explicit lines
        "horizontal_strategy": "text",  # Same for horizontal strategy
        "intersection_tolerance": 5,      # Adjust as needed
    }
    custom_settings = {}
    
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
    debug_pdf(pdf_file, 'debug_page'+str(num)+'.png')
    #raw_data = extract_table_from_pdf('debug_page'+str(num)+'.png')
    # Optionally, inspect the raw data
    #for row in raw_data[:20]:
    #    print(row)
