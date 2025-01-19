import sys
from data_parser import extract_data as ed


if __name__ == '__main__':
    
    files = [0,1,3]
    dataDirectory = {}
    for num in files:
        pdf_file = 'pdfData/Untitled'+str(num)+'.pdf'
        data = ed.data_extract_and_clean_pipeline(pdf_file)
        dataDirectory[num] = data
        print(data)
    
