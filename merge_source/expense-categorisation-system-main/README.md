# Expense Categorisation System

A local, privacy-focused tool to categorize bank transactions and detect spending anomalies.

## Features
- **Upload CSV**: Drag and drop your bank statement.
- **Financial Insights**:
    - **Health Score**: Get a 0-100 score on your financial habits.
    - **Investment Suggestions**: Personalized tips based on your savings rate.
    - **Goal Tracker**: Set and track progress towards financial goals.
    - **Spending Trends**: Analyze daily spending patterns.
- **Auto-Categorization**: Uses a Hybrid approach:
    - **Keyword Matching**: Instant categorization for common merchants.
    - **Machine Learning**: Random Forest model trained on TF-IDF features.
    - **Interactive Training**: Correct categories in the UI and click "Retrain" to improve the model instantly.
- **Anomaly Detection**: Uses Isolation Forest to flag unusual transaction amounts.
- **Visualization**: View spending breakdown by category and transaction counts.

## Installation

1.  Clone the repository.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

Run the Streamlit app:
```bash
streamlit run app.py
```
