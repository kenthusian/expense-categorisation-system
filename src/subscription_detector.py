import pandas as pd  # type: ignore
from datetime import timedelta

class SubscriptionDetector:
    def __init__(self):
        pass

    def detect_subscriptions(self, df):
        """
        Identifies potential recurring subscriptions or bills.
        
        Logic:
        1. Group by description (or normalized description).
        2. Filter groups with at least 2 transactions.
        3. Check if amounts are consistent (low variance).
        4. Check if dates are approximately monthly (25-35 days gap).
        
        Returns:
            DataFrame of detected subscriptions with average amount, frequency, and next expected date.
        """
        if df.empty or 'date' not in df.columns or 'description' not in df.columns or 'amount' not in df.columns:
            return pd.DataFrame()

        # Ensure date is datetime
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'])
        
        # Filter for expenses only (negative amounts)
        expenses = df[df['amount'] < 0].copy()
        
        subscription_candidates = []
        
        # Group by description
        grouped = expenses.groupby('description')
        
        for name, group in grouped:
            if len(group) < 2:
                continue
                
            # Verify amount consistency (std dev of amount should be low relative to mean)
            amounts = group['amount'].abs()
            mean_amount = amounts.mean()
            std_amount = amounts.std()
            
            # Allow some fluctuation (e.g., utility bills vary, but Netflix is exact)
            # Coefficient of variation < 0.1 for strict, < 0.2 for looser
            # Let's say if std_dev is less than 10% of mean, it's consistent enough for a "Fixed" sub.
            # If it varies more, it might be a "Variable" recurring bill (like utilities).
            is_fixed_amount = True
            if std_amount > 0 and (std_amount / mean_amount) > 0.1:
                is_fixed_amount = False
                
            # Check Date Intervals
            group = group.sort_values('date')
            dates = group['date'].dt.date.tolist()
            intervals = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
            
            avg_interval = sum(intervals) / len(intervals)
            
            # Monthly definition: 25 to 35 days
            is_monthly = 25 <= avg_interval <= 35
            
            if is_monthly:
                next_date = group['date'].max() + timedelta(days=int(avg_interval))
                
                subscription_candidates.append({
                    'Description': name,
                    'Avg Amount': round(mean_amount, 2),
                    'Frequency': 'Monthly',
                    'Type': 'Fixed' if is_fixed_amount else 'Variable',
                    'Next Expected': next_date.strftime('%Y-%m-%d'),
                    'Confidence': 'High' if is_fixed_amount else 'Medium'
                })
                
        return pd.DataFrame(subscription_candidates)
