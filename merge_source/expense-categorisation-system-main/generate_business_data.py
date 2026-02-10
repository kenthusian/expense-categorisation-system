import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Configuration
# Configuration
start_date = datetime(2021, 4, 1) # Start of 5-year period
end_date = datetime(2026, 3, 31)
GENERATE_LOSS = False  # Toggle this to True to generate a loss scenario

# GST Rates
GST_RATES = [0, 5, 12, 18, 28]

# Business Categories & Descriptions
descriptions = {
    'Revenue': {
        'descriptions': ['Client Payment - Project A', 'Consulting Fees', 'Product Sales', 'Service Contract Q2', 'Ad Revenue', 'Online Store Sales'],
        'gst_rate': [18], # Services usually 18%
        'type': 'Income'
    },
    'Rent': {
        'descriptions': ['Office Rent - Downtown', 'Co-working Space Fee', 'Warehouse Lease'],
        'gst_rate': [18],
        'type': 'Expense'
    },
    'Utilities': {
        'descriptions': ['Electricity Bill', 'Water Charges', 'Internet - Fiber Optic', 'Phone & Communication'],
        'gst_rate': [0, 5, 18], # Elec often 0/exempt, Internet 18
        'type': 'Expense'
    },
    'Office Supplies': {
        'descriptions': ['Staples Order', 'Printer Paper', 'Toner Cartridges', 'Desk Organizers', 'Whiteboard Markers'],
        'gst_rate': [12, 18],
        'type': 'Expense'
    },
    'Professional Services': {
        'descriptions': ['Legal Consultation', 'Accounting Audit', 'HR Consultant', 'Marketing Agency Fees'],
        'gst_rate': [18],
        'type': 'Expense'
    },
    'Travel': {
        'descriptions': ['Flight to Mumbai', 'Hotel Stay - Client Visit', 'Uber/Ola Rides', 'Train Tickets'],
        'gst_rate': [5, 12, 18],
        'type': 'Expense'
    },
    'Software': {
        'descriptions': ['AWS Cloud Bill', 'SaaS Subscription (Jira)', 'Adobe Creative Cloud', 'Zoom Pro License', 'Microsoft 365'],
        'gst_rate': [18],
        'type': 'Expense'
    },
    'Marketing': {
        'descriptions': ['Google Ads Campaign', 'Facebook Ads', 'LinkedIn Promo', 'Print Media Ad'],
        'gst_rate': [18],
        'type': 'Expense'
    },
    'Hardware': {
        'descriptions': ['New Laptop (Dell)', 'Monitor Screen', 'Server Rack Equipment', 'Mouse & Keyboards'],
        'gst_rate': [18],
        'type': 'Expense'
    },
    'Other': {
        'descriptions': ['Coffee for Pantry', 'Cleaning Services', 'Repairs & Maintenance', 'Diwali Gifts'],
        'gst_rate': [5, 12, 18],
        'type': 'Expense'
    },
    'Depreciation': {
        'descriptions': ['Asset Depreciation - IT', 'Furniture Depreciation', 'Vehicle Depreciation'],
        'gst_rate': [0], # Non-cash expense, technically no GST impact on the expense entry itself usually in simplified view
        'type': 'Expense'
    },
    'Interest': {
        'descriptions': ['Bank Loan Interest', 'Overdraft Interest', 'Credit Line Charge'],
        'gst_rate': [0], # Financial services often exempt or different
        'type': 'Expense'
    }
}

data = []
current_date = start_date

while current_date <= end_date:
    
    year_progress = (current_date.year - start_date.year)
    growth_factor = 1.0 + (year_progress * 0.15) # 15% growth per year
    
    # 1. Monthly Fixed Expenses (1st - 5th)
    if current_date.day == 5:
        # Rent (Increase with time)
        rent_amt = 50000.0 * growth_factor
        rent_gst = 18
        gst_val = rent_amt * (rent_gst/100)
        total = rent_amt + gst_val
        data.append([current_date.strftime('%Y-%m-%d'), 'Office Rent', -total, 'Rent', rent_gst, gst_val])
        
    if current_date.day == 10:
        # Utilities
        amt = random.uniform(3000, 8000) * growth_factor
        gst = 18 
        gst_val = amt * (gst/100)
        total = amt + gst_val
        data.append([current_date.strftime('%Y-%m-%d'), 'Monthly Internet & Phone', -total, 'Utilities', gst, gst_val])

    if current_date.day == 28:
        # Depreciation (Monthly entry)
        dep_amt = 15000.0 * (1 + year_progress*0.05) # Assets grow slower
        data.append([current_date.strftime('%Y-%m-%d'), 'Monthly Asset Depreciation', -dep_amt, 'Depreciation', 0, 0])
        
        # Interest
        int_amt = 8000.0 * (1 - year_progress*0.1) # Debts go down? Or up? Let's say down.
        if int_amt < 1000: int_amt = 1000
        data.append([current_date.strftime('%Y-%m-%d'), 'Bank Loan Interest', -int_amt, 'Interest', 0, 0])

    # 2. Daily Transactions (Probabilistic)
    # Higher volume for business than personal
    daily_transactions = random.randint(0, 5)
    if random.random() < 0.3 * growth_factor: daily_transactions += 1 # More volume over years
    
    for _ in range(daily_transactions):
        # Pick category
        cat_key = random.choice(list(descriptions.keys()))
        cat_info = descriptions[cat_key]
        
        # Don't do Rent/Utilities/Dep/Int again randomly too often
        if cat_key in ['Rent', 'Utilities', 'Depreciation', 'Interest']: continue
        
        desc = random.choice(cat_info['descriptions'])
        
        # Amount logic
        base_amount = 0
        if cat_key == 'Revenue': 
            if GENERATE_LOSS:
                base_amount = random.uniform(1000, 5000) 
            else:
                base_amount = random.uniform(50000, 300000) # Increased to boost profit
        elif cat_key == 'Software': base_amount = random.uniform(500, 5000)
        elif cat_key == 'Travel': base_amount = random.uniform(200, 15000)
        elif cat_key == 'Hardware': base_amount = random.uniform(5000, 80000)
        elif cat_key == 'Marketing': base_amount = random.uniform(1000, 20000)
        else: base_amount = random.uniform(100, 5000)

        # Apply Growth
        base_amount = base_amount * growth_factor

        if GENERATE_LOSS and cat_key != 'Revenue':
             base_amount = base_amount * 2.5 # Increase expenses significantly
        
        # Determine GST Rate
        gst_rate = random.choice(cat_info['gst_rate'])
        
        # Calculate GST
        gst_amount = base_amount * (gst_rate / 100)
        total_amount = base_amount + gst_amount
        
        # Sign (Income vs Expense)
        final_amount = total_amount if cat_info['type'] == 'Income' else -total_amount
        
        data.append([
            current_date.strftime('%Y-%m-%d'),
            desc,
            round(final_amount, 2),
            cat_key,
            gst_rate,
            round(gst_amount, 2)
        ])
        
    current_date += timedelta(days=1)

# Create DataFrame
columns = ['date', 'description', 'amount', 'manual_category', 'gst_rate', 'gst_amount']
df = pd.DataFrame(data, columns=columns)

# Save
df.to_csv('dummy_business_data.csv', index=False)
print(f"Generated {len(df)} business transactions.")
