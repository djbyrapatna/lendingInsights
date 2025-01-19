from transformers import pipeline

DEFAULT_MODEL = "valhalla/distilbart-mnli-12-3"
DEFAULT_CANDIDATE_LABELS = ["Rent", "Salary", "Utilities", "Transfer", "Food", "Other"]
DEFAULT_CONTEXT = 'These are bank transaction statements: '

# Initialize the zero-shot classifier.
def create_classifier_pipeline(model_name = DEFAULT_MODEL):
    classifier = pipeline("zero-shot-classification", model=DEFAULT_MODEL)
    return classifier

def classify_cluster_description(description, candidate_labels, model_name = DEFAULT_MODEL):
    """
    Uses a zero-shot classifier to assign a category to a cluster description.
    
    Parameters:
        description (str): The aggregated text from a transaction cluster.
        candidate_labels (list): A list of candidate labels (e.g., ["Rent", "Salary", "Utilities", "Transfer", "Other"]).
    
    Returns:
        str: The predicted category (the label with the highest score).
    """
    classifier = create_classifier_pipeline(model_name = model_name)

    result = classifier(description, candidate_labels, multi_label=False)
    return result["labels"][0]

def assign_categories_to_clusters(df, text_column="Transaction Description", context = DEFAULT_CONTEXT,
                                  candidate_labels = DEFAULT_CANDIDATE_LABELS, model_name = DEFAULT_MODEL):
    """
    For each unique cluster in the DataFrame, determine a category using the keywords
    extracted from that cluster. Then, assign the corresponding category to all rows
    in that cluster.
    
    Returns: A new DataFrame with a 'Category' column.
    """
    cluster_to_category = {}
    clusters = df["Cluster"].unique()
    
    for cluster_label in clusters:
        # Aggregate the texts for the cluster.
        cluster_texts = df[df["Cluster"] == cluster_label][text_column].dropna().tolist()
        # Combine a representative sample into one string. 
        aggregated_text = " ".join(cluster_texts)
        # Classify the aggregated text.
        category = classify_cluster_description(aggregated_text, candidate_labels, model_name)
        cluster_to_category[cluster_label] = category
        #print(f"Cluster {cluster_label} mapped to Category: {category}")
    
    # Create a new column in the DataFrame based on the cluster to category mapping.
    df = df.copy()
    df["Category"] = df["Cluster"].map(cluster_to_category)
    return df
    