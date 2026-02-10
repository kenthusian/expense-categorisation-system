import pandas as pd  # type: ignore
from sklearn.feature_extraction.text import TfidfVectorizer  # type: ignore
from sklearn.ensemble import RandomForestClassifier  # type: ignore
from sklearn.ensemble import IsolationForest  # type: ignore
import numpy as np  # type: ignore
import joblib  # type: ignore
import os
import re

class ExpenseCategorizer:
    def __init__(self, model_path='expense_model.pkl'):
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.clf = RandomForestClassifier(n_estimators=100, random_state=42)
        self.is_trained = False
        self.model_path = model_path
        self.confidence_threshold = 0.4
        
        # Simple rule-based fallback for the MVP to show immediate value
        self.keywords = {
            # Utilities
            'electric': 'Utilities', 'water': 'Utilities', 'internet': 'Utilities', 'phone': 'Utilities',
            'mobile': 'Utilities', 'bill': 'Utilities', 'power': 'Utilities', 'energy': 'Utilities',
            'broadband': 'Utilities', 'wifi': 'Utilities', 'cable': 'Utilities', 'adsl': 'Utilities',
            'vodafone': 'Utilities', 'airtel': 'Utilities', 'jio': 'Utilities', 'bsnl': 'Utilities',
            'electricity': 'Utilities', 'gas bill': 'Utilities', 'utility': 'Utilities',
            # Health
            'pharmacy': 'Health', 'doctor': 'Health', 'medical': 'Health', 'gym': 'Health',
            'fitness': 'Health', 'yoga': 'Health', 'hospital': 'Health', 'care': 'Health',
            'dental': 'Health', 'clinic': 'Health', 'therapy': 'Health', 'medication': 'Health',
            'apollo': 'Health', 'medplus': 'Health', '1mg': 'Health', 'pharmeasy': 'Health',
            'cult': 'Health', 'fit': 'Health', 'lab': 'Health', 'diagnostic': 'Health', 'dr.': 'Health',
            # Housing
            'rent': 'Housing', 'mortgage': 'Housing', 'apartment': 'Housing', 'housing': 'Housing',
            'lease': 'Housing', 'landlord': 'Housing', 'society': 'Housing', 'aintenance': 'Housing',
            'furniture': 'Housing', 'decor': 'Housing', 'home': 'Housing', 'repair': 'Housing',
            'painting': 'Housing', 'plumber': 'Housing', 'electrician': 'Housing',
            # Shopping
            'amazon': 'Shopping', 'walmart': 'Shopping', 'ebay': 'Shopping', 'flipkart': 'Shopping',
            'myntra': 'Shopping', 'ajio': 'Shopping', 'meesho': 'Shopping', 'nykaa': 'Shopping',
            'clothing': 'Shopping', 'shoes': 'Shopping', 'electronics': 'Shopping', 'apparel': 'Shopping',
            'mall': 'Shopping', 'ikea': 'Shopping', 'store': 'Shopping', 'shop': 'Shopping',
            'gift': 'Shopping', 'best buy': 'Shopping', 'bestbuy': 'Shopping', 'chroma': 'Shopping',
            'reliance digital': 'Shopping', 'croma': 'Shopping', 'decathlon': 'Shopping',
            'zara': 'Shopping', 'h&m': 'Shopping', 'uniqlo': 'Shopping', 'trends': 'Shopping',
            'pantaloons': 'Shopping', 'westside': 'Shopping', 'lifestyle': 'Shopping',
            'cosmetics': 'Shopping', 'beauty': 'Shopping', 'accessories': 'Shopping',
            # Food & Dining
            'grocery': 'Food', 'groceries': 'Food', 'supermarket': 'Food', 'burger': 'Food',
            'pizza': 'Food', 'bakery': 'Food', 'meat': 'Food', 'vegetable': 'Food', 'fruit': 'Food',
            'pet food': 'Food', 'food': 'Food', 'market': 'Food', 'mandi': 'Food',
            'bigbasket': 'Food', 'blinkit': 'Food', 'zepto': 'Food', 'instamart': 'Food', 'swiggy instamart': 'Food',
            'restaurant': 'Dining', 'cafe': 'Dining', 'coffee': 'Dining', 'starbucks': 'Dining',
            'mcdonalds': 'Dining', 'mcdonald': 'Dining', 'kfc': 'Dining', 'subway': 'Dining',
            'dominos': 'Dining', 'domino': 'Dining', 'zomato': 'Dining', 'swiggy': 'Dining',
            'doordash': 'Dining', 'ubereats': 'Dining', 'grubhub': 'Dining', 'eat': 'Dining',
            'takeout': 'Dining', 'dine': 'Dining', 'taco': 'Dining', 'sushi': 'Dining',
            'wendy': 'Dining', 'chipotle': 'Dining', 'dunkin': 'Dining', 'chicken': 'Dining',
            'barbeque': 'Dining', 'bistro': 'Dining', 'diner': 'Dining', 'kitchen': 'Dining',
            'chai': 'Dining', 'tea': 'Dining', 'beverage': 'Dining', 'bar': 'Dining', 'pub': 'Dining',
            # Transport
            'uber': 'Transport', 'lyft': 'Transport', 'gas': 'Transport', 'shell': 'Transport',
            'fuel': 'Transport', 'parking': 'Transport', 'metro': 'Transport', 'train': 'Transport', 'bus': 'Transport',
            'taxi': 'Transport', 'ola': 'Transport', 'toll': 'Transport', 'petrol': 'Transport', 'diesel': 'Transport',
            'cab': 'Transport', 'auto': 'Transport', 'rickshaw': 'Transport', 'bunk': 'Transport',
            'fastag': 'Transport', 'irctc': 'Transport', 'railway': 'Transport', 'flight booking': 'Transport',
            # Travel
            'flight': 'Travel', 'hotel': 'Travel', 'airbnb': 'Travel', 'vacation': 'Travel',
            'booking': 'Travel', 'airline': 'Travel', 'resort': 'Travel', 'trip': 'Travel',
            'indigo': 'Travel', 'air india': 'Travel', 'vistara': 'Travel', 'spicejet': 'Travel',
            'makemytrip': 'Travel', 'goibibo': 'Travel', 'easemytrip': 'Travel', 'cleartrip': 'Travel',
            'bnb': 'Travel', 'stay': 'Travel', 'visa': 'Travel', 'immigration': 'Travel',
            # Services
            'insurance': 'Services', 'bank': 'Services', 'subscription': 'Services',
            'laundry': 'Services', 'cleaning': 'Services', 'repair': 'Services',
            'lic': 'Services', 'policy': 'Services', 'premium': 'Services',
            'service': 'Services', 'consultancy': 'Services', 'lawyer': 'Services', 'legal': 'Services',
            'courier': 'Services', 'delivery': 'Services', 'post': 'Services', 'dhl': 'Services',
            'fedex': 'Services', 'ups': 'Services', 'urban company': 'Services', 'urbanclap': 'Services',
            # Entertainment
            'netflix': 'Entertainment', 'spotify': 'Entertainment', 'movie': 'Entertainment', 'cinema': 'Entertainment',
            'disney': 'Entertainment', 'hulu': 'Entertainment', 'youtube': 'Entertainment', 'gaming': 'Entertainment',
            'steam': 'Entertainment', 'concert': 'Entertainment', 'theater': 'Entertainment', 'theatre': 'Entertainment',
            'prime': 'Entertainment', 'hotstar': 'Entertainment', 'sonyliv': 'Entertainment', 'jiocinema': 'Entertainment',
            'bookmyshow': 'Entertainment', 'pvrcinemas': 'Entertainment', 'inox': 'Entertainment',
            'game': 'Entertainment', 'playstation': 'Entertainment', 'xbox': 'Entertainment', 'nintendo': 'Entertainment',
            'club': 'Entertainment', 'party': 'Entertainment', 'event': 'Entertainment',
            # Income
            'salary': 'Income', 'deposit': 'Income', 'refund': 'Income', 'cashback': 'Income',
            'dividend': 'Income', 'bonus': 'Income', 'freelance': 'Income', 'interest': 'Income',
            'upi received': 'Income', 'credit': 'Income', 'reimbursement': 'Income'
        }

    # ... (train/predict methods remain same) ...

    def _get_heuristic_category(self, description):
        desc_lower = str(description).lower()
        
        # 1. Exact/Partial Keyword Match using Regex (Word Boundaries)
        for key, category in self.keywords.items():
            # Use regex to match whole words and prevent partial matches
            # e.g. "bus" matches "school bus" but not "business"
            # Escape key to handle special chars if any
            pattern = r'\b' + re.escape(key) + r'\b'
            if re.search(pattern, desc_lower):
                return category
                
        # 2. Check if category name itself is in description
        # e.g. "Department of Transport" -> Transport
        possible_cats = ['Utilities', 'Health', 'Housing', 'Shopping', 'Food', 'Dining', 'Transport', 'Travel', 'Services', 'Entertainment', 'Income']
        for cat in possible_cats:
             # Also use boundaries for categories 
            pattern = r'\b' + re.escape(cat.lower()) + r'\b'
            if re.search(pattern, desc_lower):
                return cat
                
        return "Uncategorized"

    def train(self, df):
        """
        Trains the model on the provided dataframe.
        """
        # Ensure clean description
        if 'clean_description' not in df.columns:
            # Fallback if not cleaned
             if 'description' in df.columns:
                 df['clean_description'] = df['description'].astype(str).str.lower()
             else:
                 raise ValueError("Dataframe must contain 'description' or 'clean_description'.")
        
        if 'category' not in df.columns:
            raise ValueError("Dataframe must contain 'category' column for training.")

        # Filter out rows with missing descriptions or categories
        df_train = df.dropna(subset=['clean_description', 'category'])
        # Also filter out 'Unknown' or empty categories if they exist, relying on labeled data
        df_train = df_train[df_train['category'] != 'Unknown']
        
        if df_train.empty:
            print("No training data available.")
            return

        print(f"Training on {len(df_train)} records...")
        X = self.vectorizer.fit_transform(df_train['clean_description'])
        y = df_train['category']
        
        self.clf.fit(X, y)
        self.is_trained = True
        self.save_model()
        print("Model trained and saved.")

    def predict(self, df):
        """
        Predicts categories for the dataframe.
        """
        if 'clean_description' not in df.columns:
             if 'description' in df.columns:
                 df['clean_description'] = df['description'].astype(str).str.lower()
             else:
                 return df # Cannot predict

        # Load if not trained
        if not self.is_trained:
            self.load_model()

        # If still not trained, use heuristic
        if not self.is_trained:
            return self._heuristic_categorize(df)
        
        try:
            # Transform
            X = self.vectorizer.transform(df['clean_description'].fillna(''))
            
            # Predict Probabilities
            probs = self.clf.predict_proba(X)
            max_probs = np.max(probs, axis=1)
            predictions = self.clf.predict(X)
            
            # Update category column based on threshold
            # We want to keep existing categories if they are strong? 
            # Or overwrite? Users might have manually edited.
            # Ideally, we only predict for 'Unknown' or overwrite all if 'Retrain' is called.
            # But the requirement implies using ML to categorize.
            # Let's apply to all, but fallback to heuristic if confidence is low.
            
            final_cats = []
            for pred, prob, desc in zip(predictions, max_probs, df['clean_description']):
                if prob >= self.confidence_threshold:
                    final_cats.append(pred)
                else:
                    # Fallback to heuristic for this item
                    heur_cat = self._get_heuristic_category(desc)
                    # If heuristic is "Uncategorized", maybe keep the weak ML prediction or just say Unknown?
                    # Let's use the weak prediction if heuristic fails, or heuristic if it succeeds.
                    if heur_cat != "Uncategorized":
                        final_cats.append(heur_cat)
                    else:
                        final_cats.append(pred) # Trust the weak ML over nothing? Or set "Unknown"?
                        # Let's trust weak ML over nothing, it's a "best guess"
                        
            df['category'] = final_cats
            
        except Exception as e:
            print(f"Prediction failed, falling back to heuristic: {e}")
            return self._heuristic_categorize(df)
            
        return df

    def save_model(self):
        try:
            joblib.dump({'vect': self.vectorizer, 'clf': self.clf}, self.model_path)
        except Exception as e:
            print(f"Failed to save model: {e}")

    def load_model(self):
        if os.path.exists(self.model_path):
            try:
                data = joblib.load(self.model_path)
                self.vectorizer = data['vect']
                self.clf = data['clf']
                self.is_trained = True
                print("Model loaded.")
            except Exception as e:
                print(f"Failed to load model: {e}")
        else:
            print("No saved model found.")

    def _get_heuristic_category(self, description):
        desc_lower = str(description).lower()
        
        # 1. Exact/Partial Keyword Match using Regex (Word Boundaries)
        for key, category in self.keywords.items():
            # Use regex to match whole words and prevent partial matches
            # e.g. "bus" matches "school bus" but not "business"
            # Escape key to handle special chars if any
            pattern = r'\b' + re.escape(key) + r'\b'
            if re.search(pattern, desc_lower):
                return category
                
        # 2. Check if category name itself is in description
        # e.g. "Department of Transport" -> Transport
        possible_cats = ['Utilities', 'Health', 'Housing', 'Shopping', 'Food', 'Dining', 'Transport', 'Travel', 'Services', 'Entertainment', 'Income']
        for cat in possible_cats:
             # Also use boundaries for categories 
            pattern = r'\b' + re.escape(cat.lower()) + r'\b'
            if re.search(pattern, desc_lower):
                return cat
                
        return "Uncategorized"

    def _heuristic_categorize(self, df):
        """
        Simple keyword matching for initial categorization.
        """
        if 'description' in df.columns:
            df['category'] = df['description'].apply(self._get_heuristic_category)
        else:
            df['category'] = "Unknown"
        return df

class AnomalyDetector:
    def __init__(self):
        self.model = IsolationForest(contamination=0.05, random_state=42)

    def detect_anomalies(self, df):
        """
        Detects anomalies based on 'amount' using ML and statistical rules.
        """
        if df.empty:
            return df
            
        # Ensure 'amount' column exists
        amount_col = None
        for col in df.columns:
            if 'amount' in col.lower() or 'debit' in col.lower() or 'credit' in col.lower():
                amount_col = col
                break
        
        if amount_col:
            try:
                # Prepare numeric data ensuring it's absolute for stats
                df[amount_col] = pd.to_numeric(df[amount_col], errors='coerce').fillna(0)
                
                # We ONLY detect anomalies in expenses (ignore Income category)
                # This prevents salary from skewing the mean and being flagged.
                expense_mask = (df['category'].astype(str).str.lower() != 'income')
                df_expenses = df[expense_mask].copy()
                
                if df_expenses.empty:
                    df['is_anomaly'] = 1
                    df['anomaly_reason'] = ""
                    return df

                # Prepare detection data (use absolute values of expenses)
                data_stats = df_expenses[[amount_col]].abs()
                
                # 1. ML Detection (Isolation Forest) on expenses only
                df_expenses['ml_anomaly'] = self.model.fit_predict(data_stats)
                
                # 2. Rule-Based Statistical Detection (Z-Score)
                mean_val = data_stats[amount_col].mean()
                std_val = data_stats[amount_col].std()
                
                # 3. Reason Logic
                reasons = []
                final_flags = []
                
                # We loop through original DF but only flag if it's an expense
                # Map expense flags back
                exp_idx = 0
                for idx, row in df.iterrows():
                    if not expense_mask.iloc[idx]:  # type: ignore
                        final_flags.append(1)
                        reasons.append("")
                        continue
                    
                    # It's an expense
                    val = abs(row[amount_col])
                    reason = []
                    is_anomaly = False
                    
                    # Skip anomaly detection for recurring fixed-cost categories
                    row_cat = str(row.get('category', '')).lower()
                    recurring_cats = ['housing', 'rent', 'utilities', 'mortgage', 'insurance']
                    is_recurring = any(rc in row_cat for rc in recurring_cats)
                    
                    if not is_recurring:
                        # ML Flag
                        if df_expenses.iloc[exp_idx]['ml_anomaly'] == -1:
                            is_anomaly = True
                            reason.append("Unusual Pattern")
                        
                        # Statistical Flag (Z-Score) - based on expense mean/std
                        if std_val > 0:
                            z_score = abs(val - mean_val) / std_val
                            if z_score > 5:
                                is_anomaly = True
                                reason.append("Absurdly High (Z > 5)")
                            elif z_score > 3:
                                is_anomaly = True
                                reason.append("High Expense (Z > 3)")
                                
                        # Fixed threshold flag
                        if val > 10000:
                            is_anomaly = True
                            reason.append("Massive Transaction (>10k)")
                        
                    if is_anomaly:
                        final_flags.append(-1)
                        reasons.append(" & ".join(reason))
                    else:
                        final_flags.append(1)
                        reasons.append("")
                    
                    exp_idx += 1
                
                df['is_anomaly'] = final_flags
                df['anomaly_reason'] = reasons
                
            except Exception as e:
                print(f"Anomaly detection failed: {e}")
                df['is_anomaly'] = 1
                df['anomaly_reason'] = ""
        else:
             df['is_anomaly'] = 1
             df['anomaly_reason'] = ""
             
        return df
