import pandas as pd
from transformers import pipeline

def classify_transactions_in_subset(sub_df, text_column, candidate_labels, classifier, context, few_shot_prompt):
    """
    For each row in the subset DataFrame, use the classifier to assign a category
    based on the transaction description.
    
    Parameters:
      sub_df (pd.DataFrame): DataFrame containing transactions.
      text_column (str): Column with the transaction description.
      candidate_labels (list): List of candidate labels.
      classifier: A zero-shot classification pipeline.
      context: Whether or not to add context to model.
      few_shot_prompt: Optional-examples to add to help classifier.
      
    Returns:
      pd.DataFrame: The subset DataFrame with an added 'Category' column.
    """
    sub_df = sub_df.copy()
    categories = []
    
    for idx, row in sub_df.iterrows():
        description = row[text_column]
        prompt = ''
        if context:
            amount = row.get("Debit") if pd.notnull(row.get("Debit")) else row.get("Credit")
            context = f"This is a bank transaction of amount {amount}. "
            prompt = context + description
        elif few_shot_prompt is not None:
            prompt = f"{few_shot_prompt}\nTransaction:{description}\nCategory:"
        else:
            prompt = description

        
        # Run the classification.
        result = classifier(prompt, candidate_labels, multi_label=False)
        
        categories.append(result["labels"][0])
        
    sub_df["Category"] = categories
    return sub_df

def classify_transaction_descriptions_with_amounts_split_pytorch(
    df, 
    text_column="Transaction Description", 
    debit_column="Debit", 
    credit_column="Credit",
    candidate_labels=None,
    model_name="distilroberta-base-mnli",  # lightweight alternative
    context = True,
    few_shot_prompt = ''
):
    """
    Splits the input DataFrame into subsets of debit and credit transactions, then uses a 
    zero-shot classifier (based on a RoBERTa model) to directly classify each transaction.
    
    Parameters:
      df (pd.DataFrame): Input DataFrame containing at least the columns 
                         'Transaction Description', 'Debit', and 'Credit'.
      text_column (str): Column name for transaction descriptions.
      debit_column (str): Column name for the Debit values.
      credit_column (str): Column name for the Credit values.
      candidate_labels (list): List of candidate category labels. If None, a default is used.
      model_name (str): The Hugging Face model identifier for zero-shot classification.
      context (bool): Whether or not to add context to model.
      few_shot_prompt (str): Optional-examples to add to help classifier.
    
    Returns:
      pd.DataFrame: The original DataFrame with an added 'Category' column. Rows
                    with neither debit nor credit remain unclassified.
    """
    # Set default candidate labels if none are provided.
    if candidate_labels is None:
        candidate_labels = ["Rent", "Salary", "Utilities", "Transfer", "Bill Payment", "Food", "Other"]
    
    # Initialize the zero-shot classifier using the provided model.
    classifier = pipeline("zero-shot-classification", model=model_name)
    
    # Split the DataFrame into debit and credit subsets.
    debit_df = df[df[debit_column].notnull()].copy()
    credit_df = df[df[credit_column].notnull()].copy()
    # Optionally, handle rows where neither debit nor credit is present.
    other_df = df[(df[debit_column].isnull()) & (df[credit_column].isnull())].copy()
    
    # Classify each subset.
    if not debit_df.empty:
        debit_df = classify_transactions_in_subset(debit_df, text_column, candidate_labels, classifier, context, few_shot_prompt)
    if not credit_df.empty:
        credit_df = classify_transactions_in_subset(credit_df, text_column, candidate_labels, classifier,context, few_shot_prompt)
    
    # Optionally, assign a default category to rows in 'other_df'
    if not other_df.empty:
        other_df = other_df.copy()
        other_df["Category"] = "Unclassified"
    
    # Recombine the DataFrame, preserving the original order.
    combined_df = pd.concat([debit_df, credit_df, other_df]).sort_index()
    return combined_df

# ----- Example Usage -----
if __name__ == '__main__':
    # Example DataFrame with transaction descriptions and debit/credit columns.
    data = {
        "Transaction Description": [
            "Monthly Rent Payment for apartment",
            "Salary deposit for June",
            "Electricity bill for May usage",
            "Water bill for May",
            "Transfer to savings account executed",
            "BPAY for Internet subscription",
            "Payment for groceries at supermarket",
            "Rent payment for office space",
            "Salary for July credited",
            "Credit card payment for shopping",
            "Internet subscription bill for wifi",
            "Rent payment for office premises",
            "Salary credited in bank"
        ],
        "Debit": [None, None, 100, 50, None, None, None, 750, None, None, None, 800, None],
        "Credit": [None, 2000, None, None, 500, 75, 120, None, 2100, 150, 60, None, 2200]
    }
    df = pd.DataFrame(data)
    
    # Classify transactions using the modified function.
    classified_df = classify_transaction_descriptions_with_amounts_split_pytorch(
        df,
        text_column="Transaction Description",
        debit_column="Debit",
        credit_column="Credit",
        candidate_labels=["Rent", "Salary", "Utilities", "Transfer", "Bill Payment", "Food", "Other"],
        model_name="distilroberta-base-mnli"
    )
    
    print(classified_df[["Transaction Description", "Debit", "Credit", "Category"]])
