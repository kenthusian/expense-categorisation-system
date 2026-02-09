import numpy as np

def calculate_financial_health_score(total_income, total_expense, investments):
    """
    Calculates Financial Health Score (0-100) based on:
    1. Savings Ratio (40 pts): (Income - Expense) / Income >= 20%
    2. Investment Volume (30 pts): Total Invested / Income >= 20%
    3. Asset Allocation (30 pts): Proximity to Ideal (60% Stocks, 30% Bonds, 10% Commodities)

    Args:
        total_income (float): Monthly Income
        total_expense (float): Monthly Expense (Absolute value)
        investments (dict): {'stocks': float, 'bonds': float, 'commodities': float}

    Returns:
        score (int): 0-100
        details (dict): Breakdown
    """
    
    if total_income <= 0:
        return 0, {
            "savings_score": 0, "volume_score": 0, "allocation_score": 0,
            "savings_ratio": 0, "investment_ratio": 0, "net_savings": 0
        }

    # 1. Savings Score (Max 40)
    # Target: Save 20% of income
    net_savings = total_income - total_expense
    savings_ratio = max(0, net_savings / total_income)
    savings_score = min(40, (savings_ratio / 0.20) * 40)

    # 2. Investment Volume Score (Max 30)
    # Target: Invest 20% of income
    total_invested = sum(investments.values())
    investment_ratio = total_invested / total_income
    volume_score = min(30, (investment_ratio / 0.20) * 30)

    # 3. Asset Allocation Score (Max 30)
    # Ideal: Stocks 60%, Bonds 30%, Commodities 10%
    if total_invested > 0:
        actual_alloc = np.array([
            investments.get('stocks', 0) / total_invested,
            investments.get('bonds', 0) / total_invested,
            investments.get('commodities', 0) / total_invested
        ])
        target_alloc = np.array([0.60, 0.30, 0.10])
        
        # Calculate similarity/difference
        # Using 1 - Total Absolute Error / 2 (since max error sum is 2)
        # Perfect match = 1.0, Worst match (0 overlap) ~ 0
        diff = np.sum(np.abs(actual_alloc - target_alloc))
        match_quality = max(0, 1 - (diff / 2)) # Normalize to 0-1
        
        allocation_score = match_quality * 30
    else:
        allocation_score = 0
        actual_alloc = np.array([0, 0, 0])

    total_score = int(savings_score + volume_score + allocation_score)

    return total_score, {
        "savings_score": int(savings_score),
        "volume_score": int(volume_score),
        "allocation_score": int(allocation_score),
        "savings_ratio": savings_ratio * 100,
        "investment_ratio": investment_ratio * 100,
        "net_savings": net_savings,
        "total_invested": total_invested,
        "allocation": {
            "stocks": actual_alloc[0] * 100,
            "bonds": actual_alloc[1] * 100,
            "commodities": actual_alloc[2] * 100
        }
    }
