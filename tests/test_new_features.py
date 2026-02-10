import pytest
import pandas as pd
import os
from src.auth import signup_user, login_user, USERS_FILE
from src.utils import generate_pdf, generate_excel

def setup_module(module):
    """Setup for tests - ensure clean state"""
    if os.path.exists(USERS_FILE):
        os.remove(USERS_FILE)

def teardown_module(module):
    """Teardown - clean up files"""
    if os.path.exists(USERS_FILE):
        os.remove(USERS_FILE)
    if os.path.exists("test_output.pdf"):
        os.remove("test_output.pdf")
    if os.path.exists("test_output.xlsx"):
        os.remove("test_output.xlsx")

def test_auth_flow():
    # 1. Signup
    success, msg = signup_user("testuser", "password123")
    assert success is True
    assert "successful" in msg.lower()
    
    # 2. Duplicate Signup
    success, msg = signup_user("testuser", "password123")
    assert success is False
    assert "exists" in msg.lower()
    
    # 3. Login Success
    success, msg = login_user("testuser", "password123")
    assert success is True
    assert "welcome" in msg.lower()
    
    # 4. Login Failure (Wrong PW)
    success, msg = login_user("testuser", "wrongpass")
    assert success is False
    assert "incorrect" in msg.lower()
    
    # 5. Login Failure (User not found)
    success, msg = login_user("nonexistent", "pass")
    assert success is False
    assert "not found" in msg.lower()

def test_export_pdf():
    # Create dummy data
    data = {
        'date': ['2023-01-01', '2023-01-02'],
        'description': ['Salary', 'Groceries'],
        'category': ['Income', 'Food'],
        'amount': [5000, -200]
    }
    df = pd.DataFrame(data)
    
    # Generate PDF
    pdf_bytes = generate_pdf(df, "USD")
    assert len(pdf_bytes) > 0
    assert pdf_bytes.startswith(b"%PDF")
    
    # Save to verify file creation works
    with open("test_output.pdf", "wb") as f:
        f.write(pdf_bytes)
    assert os.path.exists("test_output.pdf")

def test_export_excel():
    # Create dummy data
    data = {
        'date': ['2023-01-01', '2023-01-02'],
        'description': ['Salary', 'Groceries'],
        'category': ['Income', 'Food'],
        'amount': [5000, -200]
    }
    df = pd.DataFrame(data)
    
    # Generate Excel
    excel_bytes = generate_excel(df)
    assert len(excel_bytes) > 0
    
    # Save to verify
    with open("test_output.xlsx", "wb") as f:
        f.write(excel_bytes)
    assert os.path.exists("test_output.xlsx")
