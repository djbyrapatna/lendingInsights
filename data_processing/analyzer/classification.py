import sys
from data_parser import extract_data as ed
from .createTrainingDataset import cluster_transaction_descriptions_with_amounts_split_pytorch as cluster_func
from .store_load_data import save_dict, load_dict
from .transaction_mapping import assign_categories_to_clusters as assign_rule
from .transaction_mapping_llm import assign_categories_to_clusters as assign_llm
from .transaction_mapping_llm_direct import classify_transaction_descriptions_with_amounts_split_pytorch as assign_llm_direct
import pandas as pd


def classification_pipeline(df, cluster_func, assign_func=None, **kwargs):
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
        cluster_keys = ["text_column", "debit_column", "credit_column", "num_clusters", "amount_scale", "model_name", "embedding_model_name"]
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


def run_comparison(df, **kwargs):
    """
    Calls the extraction pipeline on pdf_file and then applies three classification
    combinations.
    
    Combinations:
      1. cluster_func = cluster_func, assign_func = assign_rule
      2. cluster_func = cluster_func, assign_func = assign_llm
      3. cluster_func = assign_llm_direct, assign_func = None
      
    Then prints the original Transaction Description and the Category column for each run.
    
    Additional kwargs are passed along to the classification pipeline.
    """
    # Combination 1
    df_rule = classification_pipeline(
        df,
        cluster_func=cluster_func,  # your cluster function, assumed to be imported elsewhere
        assign_func=assign_rule,
        **kwargs
    )
    
    # Combination 2
    df_llm = classification_pipeline(
        df,
        cluster_func=cluster_func,
        assign_func=assign_llm,
        **kwargs
    )
    
    # Combination 3: assign_func is None, and we directly use the assign_llm_direct function as cluster_func.
    df_llm_direct = classification_pipeline(
        df,
        cluster_func=assign_llm_direct,
        assign_func=None,
        **kwargs
    )
    results = {
    "rule": df_rule,          # obtained earlier from assign_rule
    "llm": df_llm,            # obtained earlier from assign_llm
    "llm_direct": df_llm_direct  # obtained earlier from assign_llm_direct
    }

    # Combine the outputs based on the assumption that the rows align by index.
    # (This should be the case if the extraction pipeline preserves order.)
    comparison_df = pd.DataFrame({
        "Transaction Description": results["rule"]["Transaction Description"],
        "Rule Category": results["rule"]["Category"],
        "LLM Category": results["llm"]["Category"],
        "LLM Direct Category": results["llm_direct"]["Category"]
    })
    print(comparison_df)


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
    run_comparison(dataDirectory[1], model_name = 'facebook/bart-large-mnli')
    
    # labeledDirectory = {}
    # for key in dataDirectory.keys():
        
    #     clusters  = cluster_func(dataDirectory[key], amount_scale=.1, model_name='mgrella/autonlp-bank-transaction-classification-5521155',
    #                              num_clusters=[5,2])
    #     labeledDirectory[key] = clusters
    # save_dict(labeledDirectory, savePath)
    




    
