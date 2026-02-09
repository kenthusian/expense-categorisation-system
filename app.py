import streamlit as st
import pandas as pd
from src.data_processor import load_data, preprocess_data
from src.model import ExpenseCategorizer, AnomalyDetector
from src.utils import render_charts

st.set_page_config(page_title="Expense Categorisation System", layout="wide")

st.title("💰 Expense Categorisation System")
st.markdown("""
This application helps you categorize your expenses and detect abnormal spending patterns.
**Privacy Notice:** All processing is done locally. No data leaves your machine.
""")

# Sidebar for file upload
st.sidebar.header("Upload Data")
uploaded_file = st.sidebar.file_uploader("Upload your bank statement (CSV)", type=["csv"])

# Initialize session state for the model
if 'categorizer' not in st.session_state:
    st.session_state.categorizer = ExpenseCategorizer()

categorizer = st.session_state.categorizer

if uploaded_file is not None:
    try:
        # Load and preprocess
        df = load_data(uploaded_file)
        df = preprocess_data(df) # Ensure we call this!
        
        st.write("### Raw Data Preview")
        st.dataframe(df.head())

        # Categorization
        st.write("### Categorization")
        # categorizer is now from session_state
        
        # Check if we have a model, if not, we might need to train one or use a heuristic
        # For this MVP, we will use a simple keyword-based approach to bootstrap
        df = categorizer.predict(df)
        
        st.write("### Categorized Data (You can edit categories below)")
        # Use data_editor to allow users to fix categories
        edited_df = st.data_editor(df, num_rows="dynamic")

        # Retrain button
        if st.button("Retrain Model with My Changes"):
            try:
                # We need to preserve the state of the model. 
                # In Streamlit, this requires session_state or caching.
                # For this simple MVP, we re-instantiate, but ideally we load from pickle.
                # Let's simplify: We assume the user wants to train on THIS dataset.
                
                # Preprocess again just in case (though data_editor returns a df)
                # Ensure clean_description is there (it should be if passed in)
                
                categorizer.train(edited_df)
                st.success("Model retrained successfully! Future predictions will be better.")
                
                # Re-run prediction on the same data to show it "worked" (overfitting but confirms logic)
                # actually, we just verified it with the training.
                
                # Update the charts with new data
                df = edited_df

            except Exception as e:
                st.error(f"Training failed: {e}")

        st.write("### Categorized Data Preview")
        st.dataframe(df.head())

        # Anomaly Detection
        st.write("### Anomaly Detection")
        anomaly_detector = AnomalyDetector()
        df = anomaly_detector.detect_anomalies(df)
        
        anomalies = df[df['is_anomaly'] == -1]
        if not anomalies.empty:
            st.warning(f"Found {len(anomalies)} potential anomalies!")
            st.dataframe(anomalies)
        else:
            st.success("No anomalies detected.")

        # Visualization
        st.write("### Spending Analysis")
        render_charts(df)

    except Exception as e:
        st.error(f"Error processing file: {e}")
else:
    st.info("Please upload a CSV file to get started.")
