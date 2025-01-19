import pandas as pd
import pickle

def save_df(df, path):
    with open(path, "wb") as f:
        pickle.dump(df, f)

def save_dict(data_dict, path):
    with open(path, "wb") as f:
        pickle.dump(data_dict, f)

def load_df(path):
    with open(path, "rb") as f:
        loaded_data = pickle.load(f)
    return loaded_data

def load_dict(path):
    with open(path, "rb") as f:
        loaded_data_dict = pickle.load(f)
    return loaded_data_dict
