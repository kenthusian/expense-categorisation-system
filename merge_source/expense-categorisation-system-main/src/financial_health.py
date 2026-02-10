import numpy as np

def calculate_financial_health_score(total_income, total_expense, investments, weights=None):
    """
    Calculates Financial Health Score (0-100) based on dynamic weights.
    Default: Savings (50%), Volume (30%), Allocation (20%)
    """
    if weights is None:
        weights = {'savings': 0.5, 'volume': 0.3, 'allocation': 0.2}

    if total_income <= 0:
        return 0, {
            "savings_score": 0, "volume_score": 0, "allocation_score": 0,
            "savings_ratio": 0, "investment_ratio": 0, "net_savings": 0
        }

    # 1. Savings Score
    # Target: Save 20% of income
    net_savings = total_income - total_expense
    savings_ratio = max(0, net_savings / total_income)
    # Score out of 100 first, then apply weight
    raw_savings_score = min(100, (savings_ratio / 0.20) * 100)
    weighted_savings = raw_savings_score * weights['savings']

    # 2. Investment Volume Score
    # Target: Invest 20% of income
    total_invested = sum(investments.values())
    investment_ratio = total_invested / total_income
    raw_volume_score = min(100, (investment_ratio / 0.20) * 100)
    weighted_volume = raw_volume_score * weights['volume']

    # 3. Asset Allocation Score
    # Ideal: Stocks 60%, Bonds 30%, Commodities 10%
    if total_invested > 0:
        actual_alloc = np.array([
            investments.get('stocks', 0) / total_invested,
            investments.get('bonds', 0) / total_invested,
            investments.get('commodities', 0) / total_invested
        ])
        target_alloc = np.array([0.60, 0.30, 0.10])
        diff = np.sum(np.abs(actual_alloc - target_alloc))
        match_quality = max(0, 1 - (diff / 2)) # Normalize to 0-1
        raw_allocation_score = match_quality * 100
    else:
        raw_allocation_score = 0
        actual_alloc = np.array([0, 0, 0])
        
    weighted_allocation = raw_allocation_score * weights['allocation']

    total_score = int(weighted_savings + weighted_volume + weighted_allocation)

    return total_score, {
        "savings_score": int(weighted_savings),
        "volume_score": int(weighted_volume),
        "allocation_score": int(weighted_allocation),
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
