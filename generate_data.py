import pandas as pd  # type: ignore
import numpy as np  # type: ignore
import random
from datetime import datetime, timedelta

# Configuration
start_date = datetime(2025, 7, 1)
end_date = datetime(2026, 1, 31)
salary_amount = 4500.00
rent_amount = 1500.00

descriptions = {
    'Groceries': ['Whole Foods', 'Trader Joes', 'Safeway', 'Costco', 'Local Market'],
    'Dining': ['Starbucks', 'Chipotle', 'Local Cafe', 'McDonalds', 'Fancy Dinner Place', 'Uber Eats'],
    'Transport': ['Uber', 'Lyft', 'Shell Gas Station', 'Public Transit', 'Parking'],
    'Shopping': ['Amazon', 'Target', 'Best Buy', 'Clothing Store', 'Online Store'],
    'Entertainment': ['Netflix', 'Spotify', 'Cinema', 'Steam Games', 'Concert Ticket'],
    'Utilities': ['Electric Co', 'Water Board', 'Internet Provider', 'Mobile Bill']
}

data = []

current_date: datetime = start_date
while current_date <= end_date:
    # 1. Salary (1st of month)
    if current_date.day == 1:  # type: ignore
        data.append([current_date.strftime('%Y-%m-%d'), 'Tech Corp Salary Input', salary_amount, 'Income'])  # type: ignore
        
    # 2. Rent (5th of month)
    if current_date.day == 5:  # type: ignore
        data.append([current_date.strftime('%Y-%m-%d'), 'Luxury Apartments Rent', 0 - rent_amount, 'Rent'])  # type: ignore
        
    # 3. Utilities (15th)
    if current_date.day == 15:  # type: ignore
         data.append([current_date.strftime('%Y-%m-%d'), 'City Utility Bill', 0 - random.uniform(50, 150), 'Utilities'])  # type: ignore
    
    # 4. Random Daily Expenses (Probabilistic)
    if random.random() < 0.6: # 60% chance of distinct transaction
        cat = random.choice(list(descriptions.keys()))
        if cat == 'Utilities': continue # Handled above
        
        desc = random.choice(descriptions[cat])
        amount = 0
        
        if cat == 'Groceries': amount = random.uniform(30, 200)
        elif cat == 'Dining': amount = random.uniform(10, 80)
        elif cat == 'Transport': amount = random.uniform(10, 50)
        elif cat == 'Shopping': amount = random.uniform(20, 300)
        elif cat == 'Entertainment': amount = random.uniform(5, 60)
        
        data.append([current_date.strftime('%Y-%m-%d'), desc, 0 - round(amount, ndigits=2), cat])  # type: ignore

    # 5. Occasional Anomalies
    if random.random() < 0.005: # 0.5% chance
        data.append([current_date.strftime('%Y-%m-%d'), 'Luxury Watch Store', -5000.00, 'Shopping'])

    current_date += timedelta(days=1)


# Create DataFrame
df = pd.DataFrame(data, columns=['date', 'description', 'amount', 'manual_category']) # manual_category to help training if we wanted, but we will ignore it for the raw file usually

# Save
# Note: The app expects 'date', 'description', 'amount'. 
# We'll save just that, or maybe include category if we want to cheat for the "Verified" set.
# But for standard use, let's keep it raw.
df[['date', 'description', 'amount']].to_csv('dummy_data.csv', index=False)
print(f"Generated {len(df)} transactions.")
