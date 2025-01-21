import pandas as pd
import sys
import json
from data_parser import extract_data
from analyzer import classification, metrics, createTrainingDataset, transaction_mapping, transaction_mapping_llm, transaction_mapping_llm_direct

def document_to_loan_evaluation_pipeline(
    pdf_file, 
    cluster_func=createTrainingDataset.cluster_transaction_descriptions_with_amounts_split_pytorch,
    assign_func=transaction_mapping_llm.assign_categories_to_clusters
):
    extract_df = extract_data.data_extract_and_clean_pipeline(pdf_file)
    labeled_df = classification.classification_pipeline(extract_df, cluster_func=cluster_func, assign_func=assign_func)
    metrics_dict = metrics.aggregate_metrics(labeled_df)
    loan_eligibility_score, msg = metrics.calculate_loan_eligibility_score(metrics=metrics_dict)
    
    result = {
        "transactions": labeled_df.to_dict(orient="records"),
        "metrics": metrics_dict,
        "loan_eligibility_score": loan_eligibility_score,
        "message": msg
    }
    print(json.dumps(result, default=str))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit("Usage: python -m data_processing.pipeline.pipeline <pdf_file>")
    pdf_file = sys.argv[1]
    document_to_loan_evaluation_pipeline(pdf_file)
