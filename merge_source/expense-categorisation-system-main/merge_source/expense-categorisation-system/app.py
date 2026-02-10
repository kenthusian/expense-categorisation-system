import streamlit as st
import pandas as pd
from src.data_processor import load_data, preprocess_data
from src.model import ExpenseCategorizer, AnomalyDetector
from src.model import ExpenseCategorizer, AnomalyDetector
from src.utils import render_charts, get_random_quote
from src.goals import GoalManager
from src.financial_health import calculate_financial_health_score
import datetime

st.set_page_config(page_title="Expense Categorisation System", layout="wide")

st.title("💰 Expense Categorisation System")
st.markdown("""
This application helps you categorize your expenses and detect abnormal spending patterns.
**Privacy Notice:** All processing is done locally. No data leaves your machine.
""")

# Sidebar for file upload
st.sidebar.header("Upload Data")
uploaded_file = st.sidebar.file_uploader("Upload your bank statement (CSV)", type=["csv"])

# Sidebar Daily Quote
st.sidebar.markdown("---")
st.sidebar.subheader("🌟 Daily Motivation")
st.sidebar.info(f"_{get_random_quote()}_")

# Currency Selection
currency = st.sidebar.selectbox("Select Currency", ["USD ($)", "EUR (€)", "INR (₹)"])
currency_symbol = currency.split("(")[1].strip(")")

# --- Manual Inputs for Financial Health ---
st.sidebar.markdown("---")
st.sidebar.subheader("💰 Financial Inputs")
monthly_income = st.sidebar.number_input("Monthly Income", min_value=0.0, step=100.0, value=0.0)

st.sidebar.markdown("### 📈 Investments")
stocks_inv = st.sidebar.number_input("Invested in Stocks", min_value=0.0, step=100.0, value=0.0)
bonds_inv = st.sidebar.number_input("Invested in Bonds", min_value=0.0, step=100.0, value=0.0)
commodities_inv = st.sidebar.number_input("Invested in Commodities", min_value=0.0, step=100.0, value=0.0)

total_manual_investment = stocks_inv + bonds_inv + commodities_inv

# Navigation (Simple State)
if 'page' not in st.session_state:
    st.session_state.page = 'welcome'

def go_to_dashboard():
    st.session_state.page = 'dashboard'

if st.session_state.page == 'welcome':
    st.title("Welcome to Expense Categorisation System 💰")
    st.markdown("""
    ### Take Control of Your Finances
    
    Categorize your bank statements, detect anomalies, set financial goals, and track your financial health.
    
    **Features:**
    - 📂 **Auto-Categorization**: Upload generic CSVs and let AI sort your expenses.
    - 🔍 **Anomaly Detection**: Spot unusual transactions instantly.
    - 🎯 **Goal Tracking**: Set targets for your dream purchases.
    - 📊 **Health Score**: Get a score out of 100 on your financial habits.
    
    *Privacy First: Your data never leaves this computer.*
    """)
    st.button("Get Started 🚀", on_click=go_to_dashboard)
    st.stop() # Stop execution here for welcome page

# Initialize session state for the model
if 'categorizer' not in st.session_state:
    st.session_state.categorizer = ExpenseCategorizer()

if 'goal_manager' not in st.session_state:
    st.session_state.goal_manager = GoalManager()

categorizer = st.session_state.categorizer
goal_manager = st.session_state.goal_manager

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

# --- Financial Health Score ---
if uploaded_file is not None and 'df' in locals():
    st.markdown("---")
    st.header("❤️ Financial Health Score")
    
    # Calculate Total Expense from CSV (All amounts treated as outflow/expense if they are negative)
    # Actually, user requirement: "all the expensive will be given in csv file"
    # To be safe, let's sum all negative numbers. If positive numbers exist in CSV, we ignore them as income is manual.
    # Convert 'amount' to numeric first (handled in load/preprocess but safe to ensure)
    if 'amount' in df.columns:
        # We need to make sure we are not counting the same things twice if category inference happened.
        # But for score, we just need total.
        # Let's filter for negative amounts
        expenses_only = df[df['amount'] < 0]['amount'].sum()
        total_expense = abs(expenses_only)
    else:
        total_expense = 0
        
    investments = {
        'stocks': stocks_inv,
        'bonds': bonds_inv,
        'commodities': commodities_inv
    }
    
    score, details = calculate_financial_health_score(monthly_income, total_expense, investments)
    
    col_score, col_details = st.columns([1, 2])
    
    with col_score:
        # Custom Gauge-like display
        st.metric("Overall Score (ATS)", f"{score}/100")
        st.progress(score / 100)
        
        if score >= 80:
            st.success("Excellent! 🌟")
        elif score >= 50:
            st.info("Good! 👍")
        else:
            st.warning("Needs Improvement ⚠️")
            
    with col_details:
        st.write("#### Score Breakdown")
        
        col_d1, col_d2, col_d3 = st.columns(3)
        with col_d1:
            st.metric("Savings Ration Score", f"{details['savings_score']}/40")
            st.progress(details['savings_score'] / 40)
            st.caption(f"Savings Ratio: {details['savings_ratio']:.1f}%")
            
        with col_d2:
            st.metric("Volume Score", f"{details['volume_score']}/30")
            st.progress(details['volume_score'] / 30)
            st.caption(f"Inv. Ratio: {details['investment_ratio']:.1f}%")
            
        with col_d3:
            st.metric("Allocation Score", f"{details['allocation_score']}/30")
            st.progress(details['allocation_score'] / 30)
            st.caption("vs Ideal (60/30/10)")

        st.markdown("##### 📊 Portfolio Allocation vs Ideal")
        chart_data = pd.DataFrame({
            "Asset": ["Stocks", "Bonds", "Commodities"],
            "Your Portfolio": [details['allocation']['stocks'], details['allocation']['bonds'], details['allocation']['commodities']],
            "Ideal Portfolio": [60, 30, 10]
        })
        st.bar_chart(chart_data.set_index("Asset"))
        
        st.caption(f"Income: {currency_symbol}{monthly_income:,.2f} | Expenses: {currency_symbol}{total_expense:,.2f} | Invested: {currency_symbol}{details['total_invested']:,.2f}")

# --- Financial Goals Section ---
st.markdown("---")
st.header("🎯 Financial Goals")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Add a New Goal")
    with st.form("add_goal_form"):
        goal_name = st.text_input("Goal Name (e.g., Buy House)")
        target_amount = st.number_input("Target Amount ($)", min_value=1.0, step=100.0)
        current_saved = st.number_input("Already Saved ($)", min_value=0.0, step=100.0)
        target_date = st.date_input("Target Date", min_value=datetime.date.today())
        
        submitted = st.form_submit_button("Add Goal")
        if submitted:
            if goal_name and target_amount > 0:
                goal_manager.add_goal(goal_name, target_amount, current_saved, target_date)
                st.success(f"Goal '{goal_name}' added!")
                st.rerun()
            else:
                st.error("Please enter a valid name and target amount.")

with col2:
    st.subheader("Your Goals Tracking")
    goals = goal_manager.get_goals()
    
    if not goals.empty:
        for index, row in goals.iterrows():
            st.markdown(f"**{row['name']}** (By {row['target_date']})")
            
            # Calculate percentage
            progress = min(row['saved_amount'] / row['target_amount'], 1.0)
            st.progress(progress)
            
            
            c1, c2, c3 = st.columns([2, 2, 1])
            with c1:
                st.caption(f"{currency_symbol}{row['saved_amount']:,.2f} / {currency_symbol}{row['target_amount']:,.2f} ({progress*100:.1f}%)")
            with c2:
                # Update saving capability
                new_saved = st.number_input(f"Update Saved for {row['name']}", value=float(row['saved_amount']), key=f"goal_{index}")
                if new_saved != row['saved_amount']:
                    goal_manager.update_goal(index, new_saved)
                    st.rerun()
            with c3:
                if st.button("🗑", key=f"del_{index}"):
                    goal_manager.delete_goal(index)
                    st.rerun()
            st.divider()
    else:
        st.info("No goals set yet. Add one from the left sidebar!")

# --- Investment Nudge Section ---
if uploaded_file is not None and 'df' in locals():
    st.markdown("---")
    st.header("📈 Investment Suggestion")
    
    # Simple calculation: Income - Expenses
    # Assuming Income is positive and Expenses are negative (or we rely on category)
    # Let's try to infer from amounts
    
    try:
        # Check if we have 'amount' column
        amount_col = None
        for col in df.columns:
            if 'amount' in col.lower():
                amount_col = col
                break
        
        if amount_col:
            # Ensure numeric
            df[amount_col] = pd.to_numeric(df[amount_col], errors='coerce').fillna(0)
            
            # Recalculate based on Manual Input + Expenses
            # User Manual Income - Manual Investment - CSV Expenses
            
            # Using already calculated values from Health Score logic if available, 
            # but simpler to re-derive for this logic block or reuse.
            # let's reuse manual inputs.
            
            # Expenses are total_expense (from CSV)
            # Income is monthly_income
            # Investment is total_manual_investment
            
            net_savings = monthly_income - total_expense - total_manual_investment
            
            col_inv1, col_inv2 = st.columns(2)
            
            with col_inv1:
                st.metric("Total Manual Income", f"{currency_symbol}{monthly_income:,.2f}")
                st.metric("CSV Expenses", f"{currency_symbol}{total_expense:,.2f}", delta_color="inverse")
            
            with col_inv2:
                st.metric("Remaining Surplus", f"{currency_symbol}{net_savings:,.2f}")
                
                if net_savings > 0:
                    invest_amt = net_savings * 0.20
                    st.success(f"🎉 You have a surplus of **{currency_symbol}{net_savings:,.2f}** after expenses and investments.")
                    st.markdown(f"""
                    ### 💡 Investment Tip
                    Consider investing **20%** of your savings: **{currency_symbol}{invest_amt:,.2f}**.
                    
                    *Top Investment Options:*
                    - 📊 **Index Funds (S&P 500)**: Steady long-term growth.
                    - 🏦 **High Yield Savings**: Safe and accessible.
                    - 🏠 **REITs**: Real estate without buying property.
                    """)
                else:
                    st.warning("You are spending more than you earn (or breaking even). Focus on cutting unnecessary expenses to start investing!")
    except Exception as e:
        st.error(f"Could not calculate investment suggestions: {e}")
