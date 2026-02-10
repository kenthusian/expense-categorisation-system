import pandas as pd
from src.model import ExpenseCategorizer

def test_heuristic_categorization():
    categorizer = ExpenseCategorizer()
    df = pd.DataFrame({'description': ['Uber', 'Grocery']})
    # Mocking clean_description since it's expected by predict if we strictly enforced it, 
    # but the heuristic checks description or cols with 'desc'
    df = categorizer.predict(df)
    assert 'category' in df.columns
    assert df.iloc[0]['category'] == 'Transport'
    assert df.iloc[1]['category'] == 'Groceries'

def test_training_flow():
    categorizer = ExpenseCategorizer()
    
    # Training data
    train_data = pd.DataFrame({
        'clean_description': ['uber', 'lyft', 'kroger', 'whole foods', 'netflix'],
        'category': ['Transport', 'Transport', 'Groceries', 'Groceries', 'Entertainment']
    })
    
    categorizer.train(train_data)
    assert categorizer.is_trained
    
    # Prediction data
    test_data = pd.DataFrame({
        'clean_description': ['uber trip', 'kroger market']
    })
    
    result = categorizer.predict(test_data)
    assert result.iloc[0]['category'] == 'Transport'
    assert result.iloc[1]['category'] == 'Groceries'
