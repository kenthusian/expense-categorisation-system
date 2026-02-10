import streamlit as st
import pandas as pd
from src.data_processor import load_data, preprocess_data
from src.model import ExpenseCategorizer, AnomalyDetector
from src.utils import render_charts, get_random_quote
from src.subscription_detector import SubscriptionDetector
from src.goals import GoalManager
from src.financial_health import calculate_financial_health_score

import altair as alt

st.set_page_config(page_title="Expense Categorisation System", layout="wide")

# Theme Toggle
with st.sidebar:
    st.markdown("### 🎨 Theme Settings", unsafe_allow_html=True)
    theme = st.toggle("Dark Mode", value=False)

# Custom CSS for Theme
if theme:
    # Dark Mode CSS
    st.markdown("""
    <style>
        :root {
            --primary-color: #F63366;
            --background-color: #0E1117;
            --secondary-background-color: #262730;
            --text-color: #FAFAFA;
            --font: sans-serif;
        }
        .stApp {
            background-color: var(--background-color);
            color: var(--text-color);
        }
        .stSidebar {
            background-color: var(--secondary-background-color);
        }
        h1, h2, h3, h4, h5, h6, p, div, span, label {
            color: var(--text-color) !important;
        }
        .stMetric {
            background-color: #1E1E1E !important;
            padding: 10px;
            border-radius: 5px;
        }
    </style>
    """, unsafe_allow_html=True)
else:
    # Light Mode CSS (Default)
    st.markdown("""
    <style>
        :root {
            --primary-color: #F63366;
            --background-color: #FFFFFF;
            --secondary-background-color: #F0F2F6;
            --text-color: #31333F;
            --font: sans-serif;
        }
        .stApp {
            background-color: var(--background-color);
            color: var(--text-color);
        }
        .stSidebar {
            background-color: var(--secondary-background-color);
        }
        h1, h2, h3, h4, h5, h6, p, div, span, label {
            color: var(--text-color) !important;
        }
    </style>
    """, unsafe_allow_html=True)

st.title("💰 Expense Categorisation System")

# Sidebar - Financial Profile
st.sidebar.header("👤 Financial Profile")
currency = st.sidebar.selectbox("Select Currency", ["USD ($)", "EUR (€)", "GBP (£)", "INR (₹)", "JPY (¥)"])
currency_symbol = currency.split("(")[1].replace(")", "")
salary = st.sidebar.number_input("Monthly Income (After Tax)", min_value=0.0, value=3000.0, step=100.0)
pay_freq = st.sidebar.selectbox("Pay Frequency", ["Monthly", "Bi-Weekly", "Weekly"])

st.sidebar.markdown("### 📈 Investments")
stocks_inv = st.sidebar.number_input("Invested in Stocks", min_value=0.0, step=100.0, value=0.0)
bonds_inv = st.sidebar.number_input("Invested in Bonds", min_value=0.0, step=100.0, value=0.0)
commodities_inv = st.sidebar.number_input("Invested in Commodities", min_value=0.0, step=100.0, value=0.0)

# Scoring Preferences
with st.sidebar.expander("⚙️ Scoring Preferences"):
    st.caption("Adjust weight of each factor (Total 100%)")
    w_savings = st.slider("Savings Importance", 0, 100, 50, 5)
    w_volume = st.slider("Invest. Volume Importance", 0, 100, 30, 5)
    w_allocation = st.slider("Asset Allocation Importance", 0, 100, 20, 5)
    
    total_w = w_savings + w_volume + w_allocation
    if total_w != 100:
        st.warning(f"Total: {total_w}% (Should be 100%)")
    
    # Normalize for calculation
    weights = {
        'savings': w_savings / 100,
        'volume': w_volume / 100,
        'allocation': w_allocation / 100
    }

# Quote of the Day (Moved to sidebar)
st.sidebar.markdown("---")
quote = get_random_quote()
st.sidebar.info(f"💡 **Quote of the Day:**\n\n{quote}")

st.sidebar.markdown("---")
st.sidebar.header("Upload Data")
uploaded_file = st.sidebar.file_uploader("Upload your bank statement (CSV)", type=["csv"])

# Define Tabs
tab_dashboard, tab_analysis, tab_budget, tab_data = st.tabs(["📈 Dashboard", "🧠 Analysis", "💰 Budgeting", "📂 Data Management"])

# Initialize session state for the model
if 'categorizer' not in st.session_state:
    st.session_state.categorizer = ExpenseCategorizer()

if 'goal_manager' not in st.session_state:
    st.session_state.goal_manager = GoalManager()

categorizer = st.session_state.categorizer
goal_manager = st.session_state.goal_manager

with tab_data:
    st.header("📂 Data Management")
    if uploaded_file is not None:
        try:
            # Load and preprocess
            df = load_data(uploaded_file)
            df = preprocess_data(df) # Ensure we call this!
            
            # Predict
            df = categorizer.predict(df)
            
            # Detect Anomalies
            anomaly_detector = AnomalyDetector()
            df = anomaly_detector.detect_anomalies(df)
            
            st.success("Data processed successfully!")
            
            with st.expander("View Raw & Categorized Data", expanded=True):
                # Data Editor
                edited_df = st.data_editor(df, num_rows="dynamic", key="data_editor")
                
                if st.button("Retrain Model with Changes"):
                    try:
                        categorizer.train(edited_df)
                        st.success("Model retrained!")
                        st.session_state['current_df'] = edited_df
                        st.rerun()
                    except Exception as e:
                        st.error(f"Training failed: {e}")
            
            # Save to session state
            st.session_state['current_df'] = df

            # Anomaly Detection Preview
            anomalies = df[df['is_anomaly'] == -1]
            if not anomalies.empty:
                st.warning(f"Found {len(anomalies)} potential anomalies!")
                st.dataframe(anomalies)
            else:
                st.success("No anomalies detected.")

        except Exception as e:
            st.error(f"Error processing file: {e}")
    
    elif 'current_df' in st.session_state:
        st.info("Using previously uploaded data.")
    else:
        st.info("Please upload a CSV file to get started.")

# Check if we have data to show in other tabs
if 'current_df' in st.session_state:
    df = st.session_state['current_df']
    
    with tab_dashboard:
        st.header("Spending Overview")
        col1, col2 = st.columns(2)
        
        with col1:
             st.subheader("Expenses by Category")
             render_charts(df)
             
        with col2:
             # Income vs Expenses Logic
            # Detect Actual Income from CSV
            actual_income = df[df['category'] == 'Income']['amount'].sum()
            
            total_expense = df[df['category'] != 'Income']['amount'].abs().sum()
            
            # Compare Stated vs Actual
            if actual_income > 0:
                income_to_use = actual_income
                st.info(f"💡 Detected Monthly Income from CSV: {currency_symbol}{actual_income:,.2f} (Stated: {currency_symbol}{salary:,.2f})")
            else:
                income_to_use = salary
                st.warning(f"⚠️ No 'Income' category detected in CSV. Using Stated Income: {currency_symbol}{salary:,.2f}")

            # Create a nice metric row
            st.metric("Total Income (Actual)", f"{currency_symbol}{income_to_use:,.2f}")
            st.metric("Total Expenses", f"{currency_symbol}{total_expense:,.2f}", delta=f"-{(total_expense/income_to_use)*100:.1f}%")
            st.metric("Net Savings", f"{currency_symbol}{income_to_use-total_expense:,.2f}")

        # Trend Chart
        if 'date' in df.columns:
            st.markdown("### 📅 Daily Spending Trend")
            try:
                df['date'] = pd.to_datetime(df['date'])
                daily_spend = df[df['category'] != 'Income'].groupby('date')['amount'].sum().abs()
                st.line_chart(daily_spend)
            except Exception as e:
                st.warning("Could not parse dates for trend chart.")

    with tab_analysis:
        st.header("Financial Health & Insights")
        
        # Recurring Expenses
        st.subheader("🔄 Recurring Expenses & Subscriptions")
        detector = SubscriptionDetector()
        subs_df = detector.detect_subscriptions(df)
        
        if not subs_df.empty:
            total_fixed = subs_df[subs_df['Type'] == 'Fixed']['Avg Amount'].sum()
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Recurring", f"{currency_symbol}{subs_df['Avg Amount'].sum():.2f}")
            c2.metric("Fixed Subscriptions", f"{currency_symbol}{total_fixed:.2f}")
            c3.metric("Detected Items", len(subs_df))
            
            st.dataframe(subs_df, use_container_width=True)
            
            st.caption("Based on transaction frequency (~30 days) and amount consistency.")
        else:
            st.info("No recurring subscriptions detected yet.")

        st.markdown("---")

        # Anomaly Check
        st.subheader("⚠️ Anomaly Detection")
        anomalies = df[df['is_anomaly'] == -1]
        if not anomalies.empty:
            st.warning(f"Detected {len(anomalies)} unusual transactions.")
            st.dataframe(anomalies)
        else:
            st.success("No spending anomalies detected.")
            
        st.markdown("---")
        
        # Health Score
        st.subheader("❤️ Financial Health Score")
        
        # Calculate Total Expense (Absolute)
        total_expense_health = df[df['amount'] < 0]['amount'].abs().sum()
        
        # Investments from Sidebar
        investments = {
            'stocks': stocks_inv,
            'bonds': bonds_inv,
            'commodities': commodities_inv
        }
        
        
        # Determine Income Source (CSV vs Manual)
        # We already calculated income_to_use in the Dashboard tab, but that variable matches local scope there.
        # Let's re-evaluate here for clarity or use session state if we wanted.
        # Re-evaluating is safer:
        actual_income_health = df[df['category'] == 'Income']['amount'].sum()
        if actual_income_health > 0:
            final_income = actual_income_health
            st.info(f"Using Income from CSV: {currency_symbol}{final_income:,.2f}")
        else:
            final_income = salary
            # st.caption(f"Using Manual Income: {currency_symbol}{final_income:,.2f}")

        # Use updated calculate function with weights
        score, details = calculate_financial_health_score(final_income, total_expense_health, investments, weights)
        
        c1, c2 = st.columns([1, 2])
        with c1:
            st.metric("Overall Score", f"{score}/100")
            st.progress(score/100)
            if score >= 80:
                st.success("Excellent! 🌟")
            elif score >= 50:
                st.info("Good! 👍")
            else:
                st.warning("Needs Improvement ⚠️")
        
        with c2:
            st.write("**Score Breakdown**")
            col_d1, col_d2, col_d3 = st.columns(3)
            with col_d1:
                st.metric("Savings Ratio", f"{details['savings_score']}/{int(w_savings)}")
                st.progress(details['savings_score'] / w_savings if w_savings > 0 else 0)
            with col_d2:
                st.metric("Inv. Volume", f"{details['volume_score']}/{int(w_volume)}")
                st.progress(details['volume_score'] / w_volume if w_volume > 0 else 0)
            with col_d3:
                st.metric("Allocation", f"{details['allocation_score']}/{int(w_allocation)}")
                st.progress(details['allocation_score'] / w_allocation if w_allocation > 0 else 0)
                
            st.caption(f"Net Savings: {currency_symbol}{details['net_savings']:,.2f} | Total Invested: {currency_symbol}{details['total_invested']:,.2f}")
                
        st.markdown("---")
        st.subheader("💡 AI Investment Suggestions")
        
        suggestions = []
        
        # 1. Emergency Fund / Savings
        if details['savings_ratio'] < 20:
            deficit = (0.20 * final_income) - details['net_savings']
            suggestions.append(f"⚠️ **Boost Savings**: You are saving {details['savings_ratio']:.1f}% of your income. Aim for 20%. Try to save an extra {currency_symbol}{deficit:,.2f} this month.")
        else:
            suggestions.append("✅ **Great Saving Habit**: You are saving more than 20% of your income. Consider moving excess cash into investments.")

        # 2. Investment Volume
        if details['investment_ratio'] < 20:
            inv_deficit = (0.20 * final_income) - details['total_invested']
            suggestions.append(f"📉 **Under-Invested**: You're investing {details['investment_ratio']:.1f}% of income. To hit the 20% goal, invest an additional {currency_symbol}{inv_deficit:,.2f}.")
        
        # 3. Allocation
        stocks_pct = details['allocation']['stocks']
        if stocks_pct < 50:
            suggestions.append("📊 **Conservative Portfolio**: Your stock allocation is low (" + f"{stocks_pct:.1f}%" + "). For long-term growth, consider increasing exposure to broad market ETFs.")
        elif stocks_pct > 75:
            suggestions.append("🔥 **High Risk**: Your portfolio is very confusingly concentrated in stocks. Ensure you have some bonds or stable assets for downturn protection.")

        for sug in suggestions:
            if "⚠️" in sug or "📉" in sug or "🔥" in sug:
                st.warning(sug)
            else:
                st.info(sug)

        st.markdown("---")
        st.header("🎯 Financial Goals")
        
        # Initialize goals in session state
        if 'goals' not in st.session_state:
            st.session_state['goals'] = []
            
        col_form, col_list = st.columns([1, 2])
        
        with col_form:
            st.subheader("Add New Goal")
            with st.form("add_goal_form"):
                new_goal_name = st.text_input("Goal Name", placeholder="e.g. New Car")
                new_goal_target = st.number_input("Target Amount", min_value=1.0, value=1000.0)
                new_goal_saved = st.number_input("Already Saved", min_value=0.0, value=0.0)
                new_goal_date = st.date_input("Target Date")
                
                if st.form_submit_button("Add Goal"):
                    if new_goal_name:
                        goal_manager.add_goal(new_goal_name, new_goal_target, new_goal_saved, new_goal_date)
                        st.success(f"Added goal: {new_goal_name}")
                        st.rerun()
                    else:
                        st.error("Please enter a goal name.")
                        
        with col_list:
            st.subheader("Your Goals Tracking")
            goals_df = goal_manager.get_goals()
            
            if not goals_df.empty:
                for index, row in goals_df.iterrows():
                    with st.container():
                        c1, c2 = st.columns([3, 1])
                        c1.markdown(f"**{row['name']}** (Target: {row['target_date']})")
                        if c2.button("🗑", key=f"del_{index}"):
                            goal_manager.delete_goal(index)
                            st.rerun()
                            
                        # Progress
                        progress = min(row['saved_amount'] / row['target_amount'], 1.0)
                        st.progress(progress)
                        
                        # Stats and Update
                        c_stats, c_update = st.columns([2, 2])
                        c_stats.caption(f"{currency_symbol}{row['saved_amount']:,.2f} / {currency_symbol}{row['target_amount']:,.2f} ({progress*100:.1f}%)")
                        
                        new_saved = c_update.number_input(f"Saved", value=float(row['saved_amount']), key=f"goal_{index}", label_visibility="collapsed")
                        if new_saved != row['saved_amount']:
                            goal_manager.update_goal(index, new_saved)
                            st.rerun()
                        
                        st.divider()
            else:
                st.info("No goals set yet. Start by adding one!")

    with tab_budget:
        st.header("💰 Smart Budgeting")
        
        categories = sorted(df[df['category'] != 'Income']['category'].unique())
        
        if 'budgets' not in st.session_state:
            st.session_state['budgets'] = {}
            
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Set Monthly Limits")
            selected_cat = st.selectbox("Category", categories)
            current_limit = st.session_state['budgets'].get(selected_cat, 0.0)
            new_limit = st.number_input(f"Limit for {selected_cat} ({currency_symbol})", min_value=0.0, value=float(current_limit), step=10.0)
            
            if st.button("Set Limit"):
                st.session_state['budgets'][selected_cat] = new_limit
                st.success(f"Limit set for {selected_cat}!")
                st.rerun()
                
            with st.expander("Reset All Budgets"):
                if st.button("Clear All Limits"):
                    st.session_state['budgets'] = {}
                    st.rerun()

        with col2:
            st.subheader("Budget Tracking")
            
            if not st.session_state['budgets']:
                st.info("Set limits on the left to start tracking budgets!")
            else:
                # Calculate actual spending
                actual_spend = df[df['category'] != 'Income'].groupby('category')['amount'].sum().abs().to_dict()
                
                budget_data = []
                for cat, limit in st.session_state['budgets'].items():
                    actual = actual_spend.get(cat, 0.0)
                    pct = (actual / limit) * 100 if limit > 0 else 100
                    status = "✅ On Track"
                    if pct > 100:
                        status = "❌ Over Budget"
                    elif pct > 85:
                        status = "⚠️ Near Limit"
                        
                    budget_data.append({
                        "Category": cat,
                        "Budget": limit,
                        "Actual": actual,
                        "Status": status,
                        "Pct": pct
                    })
                
                budget_df = pd.DataFrame(budget_data)
                
                for _, row in budget_df.iterrows():
                    color = "red" if row['Pct'] > 100 else "orange" if row['Pct'] > 85 else "green"
                    st.write(f"**{row['Category']}** ({row['Status']})")
                    st.caption(f"{currency_symbol}{row['Actual']:.2f} / {currency_symbol}{row['Budget']:.2f}")
                    st.progress(min(1.0, row['Pct'] / 100))
                    if row['Pct'] > 100:
                        st.error(f"You've exceeded your budget by {currency_symbol}{row['Actual'] - row['Budget']:.2f}!")
