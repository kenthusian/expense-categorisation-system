from src.model import ExpenseCategorizer  # type: ignore
import pandas as pd  # type: ignore

def test_categorization():
    cat = ExpenseCategorizer()
    
    # Test cases that previously failed (false positives)
    data = {
        'description': [
            'Uber Trip',           # Should be Transport
            'Business Lunch',      # Should NOT be Transport (contains 'bus')
            'School Bus',          # Should be Transport (contains 'bus' as word)
            'Automatic Payment',   # Should NOT be Transport (contains 'auto')
            'Auto Rickshaw',       # Should be Transport (contains 'auto' as word)
            'Grocery Store',       # Should be Food
        ]
    }
    
    df = pd.DataFrame(data)
    print("Predicting categories...")
    df = cat.predict(df)
    
    print("\nResults:")
    for _, row in df.iterrows():
        print(f"'{row['description']}' -> {row['category']}")

if __name__ == "__main__":
    test_categorization()
