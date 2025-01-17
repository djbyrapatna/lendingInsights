import pdfplumber
import pandas as pd
import sys

def extract_table_from_pdf(pdf_path):
    data = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # Extract table(s) from the current page. 
            # You may need to adjust table settings depending on the PDF layout.
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    data.append(row)
    return data

def debug_pdf(pdf_path, img_path):
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        im = page.to_image()
        im.debug_tablefinder()
        im.save(img_path)

if __name__ == '__main__':
    num = sys.argv[1]
    pdf_file = '../pdfData/Untitled'+str(num)+'.pdf'
    debug_pdf(pdf_file, 'debug_page'+str(num)+'.png')
    #raw_data = extract_table_from_pdf('debug_page'+str(num)+'.png')
    # Optionally, inspect the raw data
    #for row in raw_data[:20]:
    #    print(row)
