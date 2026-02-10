import pandas as pd  # type: ignore

def calculate_financial_score(df, income, currency_symbol="$"):
    """
    Calculates a financial health score (0-100) based on spending habits.
    Returns the score, a breakdown, and investment suggestions.
    """
    score = 100
    breakdown = []
    suggestions = []
    
    if df.empty or 'amount' not in df.columns:
        return 0, ["No data to analyze"], []

    # 1. Savings Rate
    # Assuming income is monthly. If data covers > 1 month, we need to adjust.
    # For MVP, we assume the CSV is roughly one month or we average it.
    
    total_spent = df[df['amount'] > 0]['amount'].sum() # Assuming positive is expense, negative is income/refund
    # Wait, in our dummy data: 
    # Grocery 50.00 (Expense), Amazon -45.99 (Refund?), Salary 3000 (Income?)
    # usually bank csvs: -ve is expense, +ve is income OR columns Debit/Credit.
    # Let's standardize: 
    # In our dummy data: Salary is 3000. Expense is 50. 
    # Actually, usually Expense is negative in raw bank data, or positive in "Debit" column.
    # Let's check dummy_data.csv:
    # 2023-10-01,Grocery Store,50.00  <-- implied expense
    # 2023-10-05,Salary Deposit,3000.00 <-- implied income
    # 2023-10-06,Amazon Purchase,-45.99 <-- implied refund? 
    # This is ambiguous. Let's assume for this calculator: 
    # Category "Income" = Income. Everything else = Expense.
    
    # We rely on the model's categorization
    if 'category' in df.columns:
        income_rows = df[df['category'] == 'Income']
        expense_rows = df[df['category'] != 'Income']
        
        # Calculate totals
        # If amounts are all positive (magnitude), we just sum them.
        # If mixed signs, we need to be careful.
        # Let's assume magnitude for now, but relying on category is safer.
        
        total_expense = expense_rows['amount'].abs().sum()
        # We use the User Input Salary as the truth for "Income" foundation, 
        # but also check CSV income to see if it matches.
        
        savings = income - total_expense
        savings_rate = (savings / income) * 100 if income > 0 else 0
        
        # Scoring Logic
        if savings_rate >= 20:
            breakdown.append(f"✅ Great Savings Rate: {savings_rate:.1f}% (+20 pts)")
        elif savings_rate >= 10:
            score -= 10
            breakdown.append(f"⚠️ Moderate Savings Rate: {savings_rate:.1f}% (-10 pts)")
            suggestions.append("Try to increase your savings rate to at least 20%.")
        else:
            score -= 30
            breakdown.append(f"❌ Low Savings Rate: {savings_rate:.1f}% (-30 pts)")
            suggestions.append("Review discretionary spending. Your savings rate is critical.")

        # 2. Discretionary vs Essential (Needs 50 / Wants 30 / Savings 20)
        # We need to map categories to Needs/Wants.
        # Model categories: Transport, Groceries, Dining, Entertainment, Shopping.
        needs = ['Groceries', 'Transport', 'Utilities', 'Rent', 'Health']
        wants = ['Dining', 'Entertainment', 'Shopping', 'Travel']
        
        needs_spend = expense_rows[expense_rows['category'].isin(needs)]['amount'].abs().sum()
        wants_spend = expense_rows[expense_rows['category'].isin(wants)]['amount'].abs().sum()
        
        needs_pct = (needs_spend / income) * 100
        wants_pct = (wants_spend / income) * 100
        
        if needs_pct > 60:
            score -= 10
            breakdown.append(f"⚠️ High Fixed Costs: {needs_pct:.1f}% (-10 pts)")
            suggestions.append("Your fixed costs are high. Explore cheaper alternatives for groceries/transport.")
        
        if wants_pct > 35:
            score -= 20
            breakdown.append(f"❌ High Discretionary Spending: {wants_pct:.1f}% (-20 pts)")
            suggestions.append("Cut back on Dining/Entertainment to boost savings.")

        # 3. Anomalies Penalty
        if 'is_anomaly' in df.columns:
             anomalies = df[df['is_anomaly'] == -1]
             if not anomalies.empty:
                 score -= 5 * len(anomalies)
                 score = max(0, score) # Cap at 0
                 breakdown.append(f"⚠️ {len(anomalies)} Spending Anomalies Deteced (-{5*len(anomalies)} pts)")
                 suggestions.append("Check the flagged large transactions.")

    return max(0, score), breakdown, suggestions

def generate_spending_forecast(df, monthly_income):
    """
    Project end-of-month spending and balance based on current trends.
    """
    if df.empty or 'date' not in df.columns:
        return None
        
    # Ensure date
    df['date'] = pd.to_datetime(df['date'])
    
    # Filter for the latest month present in data
    latest_date = df['date'].max()
    current_month_df = df[
        (df['date'].dt.year == latest_date.year) & 
        (df['date'].dt.month == latest_date.month) &
        (df['category'] != 'Income')
    ].copy()
    
    if current_month_df.empty:
        return None
        
    # Stats
    days_passed = latest_date.day
    days_in_month = latest_date.days_in_month
    
    current_spend = current_month_df['amount'].abs().sum()
    
    # Avoid division by zero
    if days_passed == 0: 
        stats = {
            "projected_spend": 0,
            "projected_balance": monthly_income,
            "status": "Too early to tell"
        }
        return stats
        
    avg_daily_spend = current_spend / days_passed
    projected_total_spend = avg_daily_spend * days_in_month
    
    projected_balance = monthly_income - projected_total_spend
    
    return {
        "current_spend": current_spend,
        "avg_daily": avg_daily_spend,
        "days_left": days_in_month - days_passed,
        "projected_total_spend": projected_total_spend,
        "projected_balance": projected_balance,
        "month_name": latest_date.strftime("%B")
    }
