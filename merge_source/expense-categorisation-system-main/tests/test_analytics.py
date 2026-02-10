import pandas as pd
from src.analytics import calculate_financial_score

def test_financial_score_perfect():
    # Income 3000, Spend 1000 -> Savings 2000 (66%) -> Score 100
    df = pd.DataFrame({
        'category': ['Groceries', 'Transport'],
        'amount': [500, 500]
    })
    score, breakdown, suggestions = calculate_financial_score(df, 3000)
    assert score == 100
    assert len(suggestions) == 0

def test_financial_score_low_savings():
    # Income 3000, Spend 2900 -> Savings 100 (3.3%) -> Score < 70
    df = pd.DataFrame({
        'category': ['Rent', 'Groceries', 'Dining'],
        'amount': [2000, 500, 400]
    })
    score, breakdown, suggestions = calculate_financial_score(df, 3000)
    assert score < 80
    # Should suggest increasing savings
    assert any("savings rate" in s.lower() for s in suggestions)

def test_financial_score_high_wants():
    # Income 3000, Dining 2000 -> High wants penalty
    df = pd.DataFrame({
        'category': ['Dining'],
        'amount': [2000]
    })
    score, breakdown, suggestions = calculate_financial_score(df, 3000)
    assert score < 90
    assert any("Discretionary" in b for b in breakdown)
