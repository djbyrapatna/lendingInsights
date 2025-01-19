import sys
from data_parser import extract_data as ed
from .createTrainingDataset import export_transactions_for_labeling, cluster_transaction_descriptions_pytorch

if __name__ == '__main__':
    
    files = [0,1,3]
    dataDirectory = {}
    for num in files:
        pdf_file = 'pdfData/Untitled'+str(num)+'.pdf'
        data = ed.data_extract_and_clean_pipeline(pdf_file)

        dataDirectory[num] = data
    
    for key in dataDirectory.keys():
        
        clusters  = cluster_transaction_descriptions_pytorch(dataDirectory[key])
        print(clusters)

    
