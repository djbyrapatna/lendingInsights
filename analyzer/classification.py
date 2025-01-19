import sys
from data_parser import extract_data as ed
from .createTrainingDataset import cluster_transaction_descriptions_with_amounts_split_pytorch as cluster_func
from .store_load_data import save_dict, load_dict
from .transaction_mapping import assign_categories_to_clusters as assign_rule
from .transaction_mapping_llm import assign_categories_to_clusters as assign_llm
import pandas as pd




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
    # dataDirectory = load_dict(loadPath)
    # labeledDirectory = {}
    # for key in dataDirectory.keys():
        
    #     clusters  = cluster_func(dataDirectory[key], amount_scale=.1, model_name='mgrella/autonlp-bank-transaction-classification-5521155',
    #                              num_clusters=[5,2])
    #     labeledDirectory[key] = clusters
    # save_dict(labeledDirectory, savePath)
    labeledDictionary = load_dict(loadPath)
    comparison_frames = []
    for key, df in labeledDictionary.items():
        print(df.columns)
        # Make copies so that both functions process the same original data.
        df_rule = df.copy()
        df_llm = df.copy()
        
        # Apply both categorization functions.
        df_rule = assign_rule(df_rule)
        df_llm = assign_llm(df_llm)
        
        # Save the results in the result_frames dictionary (optional).
        #result_frames[key] = {"rule": df_rule, "llm": df_llm}
        
        # Create a new DataFrame for comparison.
        # We assume both functions add a "Category" column.
        comp_df = pd.DataFrame({
            "Transaction Description": df_rule["Transaction Description"],
            "Rule Category": df_rule["Category"],
            "LLM Category": df_llm["Category"]
        })
        # Optionally, add an identifier from the key.
        comp_df["Source"] = key
        
        comparison_frames.append(comp_df)
    for df in comparison_frames:
        print(df.head())




    
