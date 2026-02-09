import pandas as pd
import numpy as np
from src.model import AnomalyDetector

def test_anomaly_detection():
    detector = AnomalyDetector()
    
    # Create dataset with one obvious outlier
    # Normal transaction usage ~50-100
    # Outlier = 5000
    # 50 normal points, 1 outlier
    data = [50, 55, 60, 45, 100, 50, 60, 55, 40] * 10
    data.append(5000)
    df = pd.DataFrame({'amount': data})
    
    # Fit and predict (IsolationForest needs some data to fit)
    df = detector.detect_anomalies(df)
    
    assert 'is_anomaly' in df.columns
    # Check if the 5000 one is flagged (might need to check index or just presence)
    # The simple detector in model.py modifies the df in place
    
    anomalies = df[df['is_anomaly'] == -1]
    assert not anomalies.empty
    # The 5000 values should be captured
    assert anomalies['amount'].max() == 5000

def test_anomaly_detection_empty():
    detector = AnomalyDetector()
    df = pd.DataFrame({'amount': []})
    df = detector.detect_anomalies(df)
    assert 'is_anomaly' in df.columns
