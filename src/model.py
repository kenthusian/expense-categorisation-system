import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import IsolationForest
import numpy as np

class ExpenseCategorizer:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.clf = RandomForestClassifier(n_estimators=100, random_state=42)
        self.is_trained = False
        
        # Simple rule-based fallback for the MVP to show immediate value
        self.keywords = {
            'grocery': 'Groceries',
            'supermarket': 'Groceries',
            'restaurant': 'Dining',
            'cafe': 'Dining',
            'coffee': 'Dining',
            'uber': 'Transport',
            'lyft': 'Transport',
            'gas': 'Transport',
            'shell': 'Transport',
            'netflix': 'Entertainment',
            'spotify': 'Entertainment',
            'amazon': 'Shopping',
            'salary': 'Income',
            'deposit': 'Income'
        }

    def train(self, df):
        """
        Trains the model on the provided dataframe.
        """
        if 'clean_description' not in df.columns:
            raise ValueError("Dataframe must contain 'clean_description' column.")
        
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
        if 'clean_description' not in df.columns:
             # Try to clean it on the fly if not present, though app should handle this
             if 'description' in df.columns:
                 # We can't easily import clean_text here without circular imports or refactoring, 
                 # so we assume data_processor cleaned it. 
                 # Or better, we just ensure we use what we have.
                 # Let's assume it is preprocessed.
                 pass

        # If not trained, use heuristic
        if not self.is_trained:
            return self._heuristic_categorize(df)
        
        # Transform and predict
        # Handle case where tfidf is not fitted yet (should handle in train, but double check)
        try:
            X = self.vectorizer.transform(df['clean_description'].fillna(''))
            predicted_categories = self.clf.predict(X)
            
            # Update category column, but maybe keep old ones if confidence is low? 
            # For now, just overwrite
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
            for key, category in self.keywords.items():
                if key in desc_lower:
                    return category
            return "Uncategorized"

        if 'description' in df.columns:
            df['category'] = df['description'].apply(get_category)
        else:
             # Try to find a description-like column
            cols = [col for col in df.columns if 'desc' in col.lower() or 'narrative' in col.lower()]
            if cols:
                df['category'] = df[cols[0]].apply(get_category)
            else:
                df['category'] = "Unknown"
        
        return df

class AnomalyDetector:
    def __init__(self):
        self.model = IsolationForest(contamination=0.05, random_state=42)

    def detect_anomalies(self, df):
        """
        Detects anomalies based on 'amount'.
        """
        # Ensure 'amount' column exists
        amount_col = None
        for col in df.columns:
            if 'amount' in col.lower() or 'debit' in col.lower() or 'credit' in col.lower():
                amount_col = col
                break
        
        if amount_col:
            # Simple outlier detection on amount
            # Handle potential non-numeric data
            try:
                # Remove currency symbols if present? For now assume numeric
                data = df[[amount_col]].fillna(0)
                # Ensure it's numeric
                data[amount_col] = pd.to_numeric(data[amount_col], errors='coerce').fillna(0)
                
                df['is_anomaly'] = self.model.fit_predict(data)
            except Exception as e:
                print(f"Anomaly detection failed: {e}")
                df['is_anomaly'] = 1 # 1 is normal, -1 is anomaly
        else:
             df['is_anomaly'] = 1
             
        return df
