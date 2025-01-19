import torch
import torch.nn.functional as F
import pandas as pd
from transformers import AutoTokenizer, AutoModel

def _get_amount(row, debit_column="Debit", credit_column="Credit"):
    """
    Extracts the amount from the row.
      - If a Debit value exists, returns its absolute value.
      - Otherwise, if a Credit exists, returns its absolute value.
      - Otherwise returns 0.0.
    """
    try:
        if pd.notnull(row[debit_column]):
            return abs(float(row[debit_column]))
        elif pd.notnull(row[credit_column]):
            return abs(float(row[credit_column]))
        else:
            return 0.0
    except Exception:
        return 0.0


def export_transactions_for_labeling(dataDirectory, output_csv="transactions_for_labeling.csv"):
    """
    Exports all transaction data from the dataDirectory dictionary into a single CSV file.
    The dataDirectory is assumed to be a dict with DataFrame values.
    
    Parameters:
      dataDirectory (dict): Dictionary where keys map to DataFrames of transaction data.
      output_csv (str): Filename for the output CSV.
      
    Returns:
      None. The CSV is written to disk.
    """
    # Concatenate all DataFrames in the dictionary
    all_data = pd.concat(dataDirectory.values(), ignore_index=True)
    
    # Export the concatenated DataFrame to CSV.
    all_data.to_csv(output_csv, index=False)
    print(f"Exported data to {output_csv}")

def get_embeddings(texts, model_name='sentence-transformers/all-MiniLM-L6-v2', device=None):
    """
    Converts a list of texts to embeddings using a pretrained transformer.
    
    Parameters:
      texts (list of str): The transaction descriptions.
      model_name (str): The name of the pretrained model.
      device (str or torch.device): 'cuda' or 'cpu'. Automatically chosen if None.
      
    Returns:
      torch.Tensor: Embeddings tensor of shape (N, D), where N is the number of texts.
    """
    if device is None:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name).to(device)
    model.eval()

    with torch.no_grad():
        inputs = tokenizer(texts, padding=True, truncation=True, return_tensors='pt').to(device)
        outputs = model(**inputs)
        # Mean Pooling: average word embeddings, weighted by attention mask.
        embeddings = outputs.last_hidden_state  # shape (batch_size, seq_len, hidden_size)
        attention_mask = inputs['attention_mask'].unsqueeze(-1)  # shape (batch_size, seq_len, 1)
        masked_embeddings = embeddings * attention_mask.float()
        summed = torch.sum(masked_embeddings, dim=1)
        summed_mask = torch.clamp(attention_mask.sum(dim=1), min=1e-9)
        sentence_embeddings = summed / summed_mask
    
    return sentence_embeddings.cpu()

def kmeans_torch(embeddings, num_clusters, num_iters=100):
    """
    Performs k-means clustering on the embeddings.
    
    Parameters:
      embeddings (torch.Tensor): Tensor of shape (N, D)
      num_clusters (int): Number of clusters.
      num_iters (int): Maximum number of iterations.
      
    Returns:
      cluster_ids (torch.Tensor): Tensor of cluster assignments for each embedding.
      centroids (torch.Tensor): The final cluster centroids.
    """
    N, D = embeddings.shape
    # Randomly select initial centroids.
    indices = torch.randperm(N)[:num_clusters]
    centroids = embeddings[indices]

    for it in range(num_iters):
        # Compute pairwise Euclidean distances: shape (N, num_clusters)
        distances = torch.cdist(embeddings, centroids)
        # Assign clusters: index of the nearest centroid for each embedding.
        cluster_ids = torch.argmin(distances, dim=1)
        # Update centroids: average all embeddings in each cluster.
        new_centroids = torch.stack([
            embeddings[cluster_ids == k].mean(dim=0) if (cluster_ids == k).sum() > 0 else centroids[k]
            for k in range(num_clusters)
        ])
        if torch.allclose(new_centroids, centroids, atol=1e-4):
            break
        centroids = new_centroids

    return cluster_ids, centroids

def cluster_transaction_descriptions_pytorch(df, text_column="Transaction Description", num_clusters=[8,2]):
    """
    Splits the input DataFrame into subsets:
      - Rows with a non-null 'Debit'
      - Rows with a non-null 'Credit'
    Then, for each subset, it uses a pretrained transformer to generate sentence embeddings,
    applies k-means clustering (with PyTorch) to group the transaction descriptions,
    and finally recombines the results.
    
    Parameters:
      df (pd.DataFrame): The input DataFrame, which is assumed to contain at least the following columns:
                          'Transaction Description', 'Debit', and 'Credit'
      text_column (str): The column containing transaction description texts.
      num_clusters (int): The number of clusters for each subset.
    
    Returns:
      pd.DataFrame: The DataFrame with an added 'Cluster' column.
    """
    if not isinstance(num_clusters, list) or len(num_clusters)!=2:
        print("Invalid input for num_clusters-must be list of length 2")
        return None

    def cluster_subset(sub_df, text_col, num_clusters):
        texts = sub_df[text_col].tolist()
        embeddings = get_embeddings(texts)  # (N, D) tensor of sentence embeddings.
        cluster_ids, _ = kmeans_torch(embeddings, num_clusters=num_clusters)
        sub_df = sub_df.copy()
        sub_df["Cluster"] = cluster_ids.numpy()
        return sub_df

    # Split the DataFrame into debit and credit subsets.
    debit_df = df[df["Debit"].notnull()].copy()
    credit_df = df[df["Credit"].notnull()].copy()
    other_df = df[(df["Debit"].isnull()) & (df["Credit"].isnull())].copy()
    
    # Process each subset if it's non-empty.
    if not debit_df.empty:
        debit_df = cluster_subset(debit_df, text_column, num_clusters[0])
    if not credit_df.empty:
        credit_df = cluster_subset(credit_df, text_column, num_clusters[1])
    
    # Optionally, you can assign a default cluster to rows in 'other_df' or leave them as is.
    # For this example, we'll leave them without a cluster.
    
    # Recombine the subsets.
    combined_df = pd.concat([debit_df, credit_df, other_df]).sort_index()
    return combined_df

def cluster_transaction_descriptions_with_amounts_split_pytorch(
    df, 
    text_column="Transaction Description", 
    debit_column="Debit", 
    credit_column="Credit",
    num_clusters=[8, 2], 
    amount_scale=1.0,
    model_name = 'sentence-transformers/all-MiniLM-L6-v2'
):
    """
    Splits the input DataFrame into two subsets:
      - Debit transactions (where the Debit column is not null)
      - Credit transactions (where the Credit column is not null)
    For each subset, it obtains transformer-based text embeddings for the
    transaction description and extracts a numeric transaction amount.
    It then scales and concatenates the amount (1D) onto the text embeddings to form a combined feature vector.
    K-means clustering is applied using PyTorch on each subset separately.
    
    Parameters:
      df (pd.DataFrame): Input DataFrame with at least 'Transaction Description', 'Debit', and 'Credit' columns.
      text_column (str): Name of the transaction description column.
      debit_column (str): Name of the debit amount column.
      credit_column (str): Name of the credit amount column.
      num_clusters (list or tuple): A two-element list/tuple where the first element is the number of clusters
                                    for the debit subset, and the second is for the credit subset.
      amount_scale (float): Scaling factor for the numeric amount.
      model_name (str): The name of the pretrained model.
    
    Returns:
      pd.DataFrame: The original DataFrame with an added 'Cluster' column for clustered transactions.
                  Rows that have neither debit nor credit remain unclustered.
    """
    # Define a helper function to cluster a given subset
    def cluster_subset(sub_df, n_clusters):
        # Ensure text descriptions are available.
        texts = sub_df[text_column].fillna("").tolist()
        text_embeddings = get_embeddings(texts, model_name=model_name)  # shape: (N, D)
        
        # Extract the numeric amount for each row.
        amounts = sub_df.apply(lambda row: _get_amount(row, debit_column, credit_column), axis=1)
        amounts = torch.tensor(amounts.values, dtype=torch.float32).unsqueeze(1)  # shape: (N, 1)
        amounts = amounts * amount_scale
        
        # Concatenate text embeddings and amounts into a combined feature vector.
        combined_features = torch.cat([text_embeddings, amounts], dim=1)  # shape: (N, D+1)
        
        # Run k-means clustering on the combined features.
        cluster_ids, _ = kmeans_torch(combined_features, num_clusters=n_clusters)
        
        # Assign cluster labels to the subset.
        sub_df = sub_df.copy()
        sub_df["Cluster"] = cluster_ids.numpy()
        return sub_df
    
    # Split the DataFrame into debit and credit subsets.
    debit_df = df[df[debit_column].notnull()].copy()
    credit_df = df[df[credit_column].notnull()].copy()
    # Rows with neither debit nor credit can be left aside (or cluster them differently if desired).
    other_df = df[(df[debit_column].isnull()) & (df[credit_column].isnull())].copy()
    
    # Cluster each subset using the provided number of clusters.
    if not debit_df.empty:
        debit_df = cluster_subset(debit_df, n_clusters=num_clusters[0])
    if not credit_df.empty:
        credit_df = cluster_subset(credit_df, n_clusters=num_clusters[1])
    
    # Recombine the DataFrame in the original order.
    combined_df = pd.concat([debit_df, credit_df, other_df]).sort_index()
    return combined_df
