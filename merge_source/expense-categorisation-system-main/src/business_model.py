import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
import numpy as np

class BusinessExpenseCategorizer:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.clf = RandomForestClassifier(n_estimators=100, random_state=42)
        self.is_trained = False
        
        # Business-specific Keywords
        self.keywords = {
            'Revenue': ['client', 'payment', 'consulting', 'sales', 'contract', 'invoice', 'income', 'revenue'],
            'Rent': ['rent', 'lease', 'office space', 'coworking'],
            'Utilities': ['electric', 'water', 'internet', 'broadband', 'phone', 'telecom', 'power'],
            'Office Supplies': ['staples', 'paper', 'toner', 'ink', 'desk', 'pen', 'stationery'],
            'Professional Services': ['legal', 'accountant', 'audit', 'consultant', 'agency', 'hr', 'recruiting'],
            'Travel': ['flight', 'hotel', 'uber', 'ola', 'taxi', 'train', 'ticket', 'lodging', 'airfare'],
            'Software': ['aws', 'cloud', 'subscription', 'saas', 'adobe', 'jira', 'slack', 'zoom', 'microsoft'],
            'Marketing': ['ads', 'google', 'facebook', 'linkedin', 'promo', 'advertising', 'media'],
            'Hardware': ['laptop', 'monitor', 'keyboard', 'mouse', 'server', 'computer', 'dell', 'macbook'],
            'Cost of Goods Sold': ['material', 'inventory', 'shipping', 'freight'],
            'Employee Benefits': ['insurance', 'medical', 'bonus', 'perks'],
            'Taxes': ['gst', 'tax', 'duty', 'levy']
        }

    def train(self, df):
        """
        Trains the model on the provided dataframe.
        """
        if 'clean_description' not in df.columns:
            # Fallback if clean_description isn't there
            if 'description' in df.columns:
                 df['clean_description'] = df['description'].fillna('').astype(str).str.lower()
            else:
                 raise ValueError("Dataframe must contain 'clean_description' or 'description' column.")
        
        if 'category' not in df.columns:
            raise ValueError("Dataframe must contain 'category' column for training.")

        # Filter out rows with missing descriptions or categories
        df_train = df.dropna(subset=['clean_description', 'category'])
        
        if df_train.empty:
            return

        X = self.vectorizer.fit_transform(df_train['clean_description'])
        y = df_train['category']
        
        self.clf.fit(X, y)
        self.is_trained = True

    def predict(self, df):
        """
        Predicts categories for the dataframe.
        """
        # Ensure clean_description exists
        if 'clean_description' not in df.columns:
             if 'description' in df.columns:
                 df['clean_description'] = df['description'].fillna('').astype(str).str.lower()
             else:
                 return df

        # If not trained, use heuristic
        if not self.is_trained:
            return self._heuristic_categorize(df)
        
        try:
            X = self.vectorizer.transform(df['clean_description'].fillna(''))
            predicted_categories = self.clf.predict(X)
            df['category'] = predicted_categories
        except Exception as e:
            print(f"Prediction failed, falling back to heuristic: {e}")
            return self._heuristic_categorize(df)
            
        return df

    def _heuristic_categorize(self, df):
        """
        Simple keyword matching for initial categorization.
        """
        def get_category(description):
            desc_lower = str(description).lower()
            for cat, keywords in self.keywords.items():
                for k in keywords:
                    if k in desc_lower:
                        return cat
            return "Other"

        if 'description' in df.columns:
            df['category'] = df['description'].apply(get_category)
        
        return df
