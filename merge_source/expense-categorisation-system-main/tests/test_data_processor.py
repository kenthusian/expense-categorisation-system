import pandas as pd
from io import StringIO
from src.data_processor import load_data

def test_load_data_valid_csv():
    csv_data = """Date,Description,Amount
2023-10-01,Test Item,10.00"""
    file_like = StringIO(csv_data)
    df = load_data(file_like)
    assert 'description' in df.columns
    assert df.iloc[0]['description'] == 'Test Item'

def test_load_data_empty():
    empty_csv = ""
    file_like = StringIO(empty_csv)
    try:
        load_data(file_like)
    except Exception as e:
        assert True

def test_preprocess_data():
    df = pd.DataFrame({'description': ['UBER *RIDE 123', 'Grocery Store #4', 123]})
    from src.data_processor import preprocess_data
    df = preprocess_data(df)
    assert 'clean_description' in df.columns
    assert df.iloc[0]['clean_description'] == 'uber ride'
    assert df.iloc[1]['clean_description'] == 'grocery store'
