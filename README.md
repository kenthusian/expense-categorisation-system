# Expense Categorisation System

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-FF4B4B)
![Scikit-Learn](https://img.shields.io/badge/ML-Scikit--Learn-orange)


A **privacy-focused, local-first** application that leverages Machine Learning to categorize bank transactions, detect spending anomalies, and provide actionable financial insights.

> **Note:** This project processes all data locally on your device. No sensitive banking data is sent to the cloud.

---

## Key Features

### Intelligent Categorization
*   **Hybrid Approach:** Combines **Keyword Matching** for deterministic accuracy with a **Random Forest Classifier** for intelligent prediction of unknown merchants.
*   **Interactive Learning:** The model improves over time. Users can correct a category in the UI, and the system retrains instantly to learn from the feedback.
*   **TF-IDF Vectorization:** Converts transaction descriptions into meaningful features for the ML model.

### Financial Insights Dashboard
*   **Financial Health Score:** Calculates a 0-100 score based on savings rate, spending consistency, and budget adherence.
*   **Smart Suggestions:** Provides personalized investment tips (e.g., "Consider an Index Fund" or "Build an Emergency Fund") dynamically based on financial health.
*   **Goal Tracker:** Set financial goals and track progress visually.
*   **Spending Trends:** Interactive visualizations using **Altair** and **Plotly** to spot monthly trends and category breakdowns.

### Anomaly Detection
*   **Isolation Forest Algorithm:** Automatically flags transactions that deviate significantly from normal spending patterns, helping to spot potential fraud or accidental overspending.

### File Support
*   **Drag & Drop:** Easily upload CSV bank statements.
*   **PDF Export:** Generate summaries of categorized expenses.

---

## Tech Stack

*   **Frontend:** [Streamlit](https://streamlit.io/)
*   **Data Processing:** Pandas, NumPy
*   **Machine Learning:** Scikit-learn (RandomForestClassifier, IsolationForest, TfidfVectorizer)
*   **Visualization:** Altair, Plotly, Matplotlib
*   **Utilities:** Joblib (Model persistence), FPDF (Report generation)

---

## Getting Started

### Prerequisites
*   Python 3.8 or higher installed.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/ExpenseCategorisationSystem.git
    cd ExpenseCategorisationSystem
    ```

2.  **Create a virtual environment (Recommended):**
    ```bash
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # Mac/Linux
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Running the App

Simply run the Streamlit application:
```bash
streamlit run app.py
```
Or use the provided batch script on Windows:
```bash
run_app.bat
```

The app will open in your default browser at `http://localhost:8501`.

---

## Project Structure

```
ExpenseCategorisationSystem/
├── src/                    # Source code for modular components
├── app.py                  # Main Streamlit application entry point
├── expense_model.pkl       # Serialized Machine Learning model
├── generate_data.py        # Utilities for generating dummy test data
├── requirements.txt        # Python dependency list
└── README.md               # Project documentation
```

---

## Future Improvements

*   Integration with Plaid API for real-time bank feeds.
*   Advanced budgeting features with email alerts.
*   Docker support for easy containerized deployment.
*   Mobile-responsive layout optimizations.

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

