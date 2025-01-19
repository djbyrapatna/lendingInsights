import torch
import torch.nn.functional as F
import pandas as pd
from transformers import AutoTokenizer, AutoModel

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

def cluster_transaction_descriptions_pytorch(df, text_column="Transaction Description", num_clusters=5):
    """
    Clusters transaction descriptions using PyTorch.
    1. Converts the descriptions to embeddings using a transformer.
    2. Runs k-means clustering on the embeddings.
    3. Adds a 'Cluster' column to the DataFrame.
    
    Parameters:
      df (pd.DataFrame): DataFrame containing transaction data.
      text_column (str): Column with transaction descriptions.
      num_clusters (int): Number of clusters for k-means.
      
    Returns:
      pd.DataFrame: Updated DataFrame with a 'Cluster' column.
    """
    # Convert the transaction descriptions into embeddings.
    texts = df[text_column].tolist()
    embeddings = get_embeddings(texts)
    
    # Cluster the embeddings using k-means implemented in PyTorch.
    cluster_ids, _ = kmeans_torch(embeddings, num_clusters=num_clusters)
    
    # Add the cluster assignments to the DataFrame.
    df["Cluster"] = cluster_ids.numpy()
    return df
