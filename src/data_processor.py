import pandas as pd  # type: ignore
import streamlit as st  # type: ignore

def load_data(file):
    """
    Loads data from a CSV file.
    Assumes standard bank statement columns like Date, Description, Amount.
    """
    try:
        df = pd.read_csv(file)
        # Normalize headers
        df.columns = [c.lower().strip() for c in df.columns]
        return df
    except Exception as e:
        raise ValueError(f"Failed to read CSV: {e}")

import re

def preprocess_data(df):
    """
    Preprocesses the data for the model.
    Cleans the description column.
    """
    if 'description' in df.columns:
        df['clean_description'] = df['description'].apply(clean_text)
    return df

def clean_text(text):
    """
    Cleans text by converting to lowercase and removing special characters.
    """
    if not isinstance(text, str):
        return str(text)
    
    text = text.lower()
    # Remove special characters and digits (optional, but good for categorization)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text
