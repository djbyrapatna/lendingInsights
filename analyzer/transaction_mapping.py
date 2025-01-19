import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import Counter
import numpy as np
import re

def preprocess_text(text):
    """
    Lowercase the text, remove punctuation, and strip extra whitespace.
    """
    text = text.lower()
    # Remove punctuation: you can adjust the regex as needed.
    text = re.sub(r'[^\w\s]', '', text)
    return text.strip()

def get_cluster_keywords(df, cluster_label, text_column="Transaction Description", top_n=10):
    """
    For a given cluster, aggregate the text, preprocess it, and return the top_n keywords
    based on word frequency.
    """
    cluster_texts = df[df["Cluster"] == cluster_label][text_column].dropna().tolist()
    # Combine all texts for the cluster.
    combined_text = " ".join(cluster_texts)
    processed = preprocess_text(combined_text)
    # Split into words.
    words = processed.split()
    
    word_counts = Counter(words)
    # Return the top_n most common words.
    return [word for word, count in word_counts.most_common(top_n)]

def map_cluster_to_category(keywords):
    """
    Given a list of keywords from a cluster, assign a category.
    This mapping is heuristic and can be refined over time.
    """
    # Example mapping rules
    if any(word in keywords for word in ["rent", "apartment", "lease"]):
        return "Rent"
    elif any(word in keywords for word in ["salary", "payroll", "credited"]):
        return "Salary"
    elif any(word in keywords for word in ["bill", "bpay", "utility", "electricity", "water", "phone", "fone"]):
        return "Utilities"
    elif any(word in keywords for word in ["transfer"]):
        return "Transfer"
    # You can add more rules as needed.
    elif any(word in keywords for word in ["withdrawal", "cash", "wd"]):
        return "Withdrawal"
    else:
        return "Other"

def assign_categories_to_clusters(df, text_column="Transaction Description"):
    """
    For each unique cluster in the DataFrame, determine a category using the keywords
    extracted from that cluster. Then, assign the corresponding category to all rows
    in that cluster.
    
    Returns: A new DataFrame with a 'Category' column.
    """
    df = df.copy()
    clusters = df["Cluster"].unique()
    cluster_to_category = {}
    
    for cluster_label in clusters:
        keywords = get_cluster_keywords(df, cluster_label, text_column=text_column, top_n=10)
        category = map_cluster_to_category(keywords)
        cluster_to_category[cluster_label] = category
        print(f"Cluster {cluster_label} keywords: {keywords} → Mapped Category: {category}")
    
    # Create a Category column based on the mapping.
    df["Category"] = df["Cluster"].map(cluster_to_category)
    return df
