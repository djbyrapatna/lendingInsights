import sys
from data_parser import extract_data as ed
from .createTrainingDataset import cluster_transaction_descriptions_with_amounts_split_pytorch as cluster_func
from .store_load_data import save_dict, load_dict
from .transaction_mapping import assign_categories_to_clusters as assign_rule
from .transaction_mapping_llm import assign_categories_to_clusters as assign_llm
from .transaction_mapping_llm_direct import classify_transaction_descriptions_with_amounts_split_pytorch as assign_llm_direct
import pandas as pd

def classification_pipeline(df, cluster_func=None, assign_func=None, **kwargs):
    """
    Processes the input DataFrame using the provided cluster_func and (optionally) assign_func.
    
    If assign_func is not None:
      1. Check kwargs for any of these keys: 
           text_column, debit_column, credit_column, num_clusters, amount_scale, model_name.
         Pass any that exist to cluster_func along with df.
      2. The resulting DataFrame (with a "Cluster" column) is then passed to assign_func.
         For assign_func, check for these keys in kwargs: 
           text_column, context, candidate_labels, model_name, (optionally few_shot_prompt).
         Pass any that exist along with the clustered DataFrame.
      3. Drop the "Cluster" column from the resulting DataFrame and return it.
    
    If assign_func is None:
      1. Check kwargs for any of these keys: 
           text_column, debit_column, credit_column, candidate_labels, model_name, context, few_shot_prompt.
         Pass any that exist along with df to cluster_func.
      2. Return the dataframe received from cluster_func.
    """
    # If an assign_func is provided, perform clustering first then assignment.
    if assign_func is not None:
        # Collect kwargs for clustering.
        cluster_keys = ["text_column", "debit_column", "credit_column", "num_clusters", "amount_scale", "model_name"]
        cluster_args = {k: kwargs[k] for k in cluster_keys if k in kwargs}
        
        # Call the clustering function.
        cluster_df = cluster_func(df, **cluster_args)
        
        # Collect kwargs for assignment.
        assign_keys = ["text_column", "context", "candidate_labels", "model_name", "few_shot_prompt"]
        assign_args = {k: kwargs[k] for k in assign_keys if k in kwargs}
        
        # Call the assignment function (which returns a DataFrame with a "Category" column).
        assigned_df = assign_func(cluster_df, **assign_args)
        
        # Drop the "Cluster" column.
        if "Cluster" in assigned_df.columns:
            assigned_df = assigned_df.drop(columns=["Cluster"])
        return assigned_df

    else:
        # If assign_func is None, use a slightly different set of kwargs for the cluster_func.
        alt_keys = ["text_column", "debit_column", "credit_column", "candidate_labels", "model_name", "context", "few_shot_prompt"]
        alt_args = {k: kwargs[k] for k in alt_keys if k in kwargs}
        return cluster_func(df, **alt_args)



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




    
