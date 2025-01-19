import sys
from data_parser import extract_data as ed
from .createTrainingDataset import cluster_transaction_descriptions_with_amounts_split_pytorch as cluster_func
from .store_load_data import save_dict, load_dict

if __name__ == '__main__':
    loadPath = sys.argv[1]
    savePath = sys.argv[2]
    # files = [0,1,3]
    # dataDirectory = {}
    # for num in files:
    #     pdf_file = 'pdfData/Untitled'+str(num)+'.pdf'
    #     data = ed.data_extract_and_clean_pipeline(pdf_file)

    #     dataDirectory[num] = data
    # save_dict(dataDirectory, path)
    dataDirectory = load_dict(loadPath)
    for key in dataDirectory.keys():
        
        clusters  = cluster_func(dataDirectory[key], amount_scale=.1, model_name='mgrella/autonlp-bank-transaction-classification-5521155')
        print(clusters)

    
