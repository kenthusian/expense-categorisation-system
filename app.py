import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
import plotly.express as px  # type: ignore
import altair as alt  # type: ignore
import numpy as np  # type: ignore
import random
import os
from datetime import datetime, date
from src.data_processor import load_data, preprocess_data  # type: ignore
from src.model import ExpenseCategorizer, AnomalyDetector  # type: ignore
from src.utils import render_charts, get_random_quote, format_currency, convert_amount  # type: ignore
from src.subscription_detector import SubscriptionDetector  # type: ignore
from src.goals import GoalManager  # type: ignore
from src.financial_health import calculate_financial_health_score  # type: ignore
from src.advisor import FinancialAdvisor  # type: ignore
from src.analytics import generate_spending_forecast  # type: ignore
from src.gamification import BadgeManager  # type: ignore
from src.auth import signup_user, login_user  # type: ignore
from src.utils import generate_excel, generate_pdf  # type: ignore
from src.business_model import BusinessExpenseCategorizer  # type: ignore

# --- PAGE CONFIG ---
st.set_page_config(page_title="MoneyGroww", layout="wide", initial_sidebar_state="expanded")

# --- CUSTOM CSS (From ExpenseThing Reference) ---
if 'theme' not in st.session_state:
    st.session_state.theme = 'Dark'

if st.session_state.theme == 'Dark':
    bg_color = '#0E1117'
    card_color = '#262730'
    text_color = '#FAFAFA'
    secondary_bg = '#1E1E1E'
    icon_bg = '#333333'
    border_color = '#444'
else:
    bg_color = '#F4F6F9'
    card_color = '#FFFFFF'
    text_color = '#333333'
    secondary_bg = '#FFFFFF'
    icon_bg = '#F0F2F5'
    border_color = '#E0E0E0'

# Vibrant colors for random username color
VIBRANT_COLORS = ["#FF5733", "#33FF57", "#3357FF", "#F333FF", "#FF33A1", "#33FFF5", "#FF8C00", "#7FFF00", "#9932CC", "#FFD700", "#FF4500", "#00CED1", "#8A2BE2"]
if 'username_color' not in st.session_state:
    st.session_state.username_color = random.choice(VIBRANT_COLORS)

# --- PREMIUM UI/UX CSS ---
if st.session_state.theme == 'Dark':
    # Sunset Lavender Aesthetic
    bg_gradient = "linear-gradient(160deg, #0F172A 0%, #1E1B4B 50%, #312E81 100%)"
    card_bg = "rgba(30, 41, 59, 0.45)"
    card_border = "rgba(255, 255, 255, 0.12)"
    text_color = "#F8FAFC"
    sub_text = "#94A3B8"
    accent_color = "#A78BFA" # Soft Lavender
    sidebar_bg = "rgba(15, 23, 42, 0.98)"
    glass_blur = "20px"
else:
    bg_gradient = "linear-gradient(160deg, #F8FAFC 0%, #E2E8F0 100%)"
    card_bg = "rgba(255, 255, 255, 0.7)"
    card_border = "rgba(0, 0, 0, 0.05)"
    text_color = "#1E293B"
    sub_text = "#64748B"
    accent_color = "#818CF8" # Soft Indigo
    sidebar_bg = "rgba(255, 255, 255, 0.95)"
    glass_blur = "15px"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');

/* Global Background */
.stApp {{
    background: {bg_gradient} !important;
}}

h1, h2, h3, h4, h5, h6 {{
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: -0.03em !important;
    color: {text_color} !important;
}}

.stMarkdown p, .stMarkdown li, label[data-testid="stWidgetLabel"], div[data-testid="stMetricValue"], .stButton button {{
    font-family: 'Inter', sans-serif !important;
}}

/* Sidebar Content Fix */
[data-testid="stSidebar"] .stMarkdown p {{
    font-family: 'Inter', sans-serif !important;
}}

/* 
   FIX: ZERO ICON OVERRIDES
   By NOT applying font-family to spans/generic containers, 
   Streamlit's internal icons will naturally use their native fonts.
*/

/* Fix for advisor boxes overlapping */
/* HUMANE UNIFORM CARDS */
.advisor-card {{
    background: {card_bg} !important;
    backdrop-filter: blur({glass_blur}) !important;
    border: 1px solid {card_border} !important;
    border-radius: 20px !important;
    padding: 24px !important;
    margin-bottom: 20px;
    height: 240px !important; /* UNIFORM SIZING */
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2) !important;
}}

.advisor-card:hover {{
    transform: translateY(-8px) scale(1.02);
    border-color: {accent_color}66 !important;
    box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.3) !important;
}}

/* Sidebar Styling */
[data-testid="stSidebar"] {{
    background: {sidebar_bg} !important;
    backdrop-filter: blur({glass_blur}) !important;
    border-right: 1px solid {card_border} !important;
}}

[data-testid="stSidebar"] .stMarkdown {{
    padding: 0.5rem 0;
}}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
    color: {text_color} !important;
}}

.username-color-span {{
    color: {st.session_state.username_color} !important;
    font-weight: 700;
}}

/* Premium Cards Wrapper */
div[data-testid="stMetric"], .stMetric, div.css-1r6slb0, .element-container div.stAlert {{
    background: {card_bg} !important;
    backdrop-filter: blur({glass_blur}) !important;
    border: 1px solid {card_border} !important;
    border-radius: 20px !important;
    padding: 20px !important;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.15) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}}

div[data-testid="stMetric"]:hover {{
    transform: translateY(-5px);
    border-color: {accent_color}55 !important;
    box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.2) !important;
}}

[data-testid="stMetricValue"] {{
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 800 !important;
    font-size: 2.4rem !important;
    color: {text_color} !important;
    letter-spacing: -0.02em;
}}

[data-testid="stMetricLabel"] {{
    color: {sub_text} !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}}

/* Sidebar Radio Styling */
.stRadio > div {{
    background: transparent !important;
}}

.stRadio label {{
    background: transparent !important;
    padding: 8px 12px !important;
    border-radius: 10px !important;
    transition: all 0.2s ease !important;
}}

.stRadio label:hover {{
    background: rgba(255,255,255,0.05) !important;
}}

/* Transaction & Item Boxes */
.transaction-box, .category-card {{
    background: {card_bg} !important;
    backdrop-filter: blur({glass_blur});
    border: 1px solid {card_border};
    border-radius: 16px;
    padding: 16px;
    margin-bottom: 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    transition: all 0.3s ease;
}}

.transaction-box:hover {{
    background: rgba(255,255,255,0.05) !important;
    border-color: {accent_color}55;
}}

/* Custom Tabs Modernization */
.stTabs [data-baseweb="tab-list"] {{
    gap: 8px;
    background: transparent !important;
    padding: 10px 0;
}}

.stTabs [data-baseweb="tab"] {{
    background: {card_bg} !important;
    border: 1px solid {card_border} !important;
    border-radius: 12px !important;
    color: {sub_text} !important;
    padding: 8px 20px !important;
    transition: all 0.2s ease !important;
}}

.stTabs [aria-selected="true"] {{
    background: {accent_color} !important;
    color: white !important;
    border-color: {accent_color} !important;
    box-shadow: 0 4px 12px {accent_color}44 !important;
}}

/* Buttons Styling */
.stButton > button {{
    border-radius: 12px !important;
    background: {accent_color} !important;
    color: white !important;
    border: none !important;
    padding: 10px 24px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 14px {accent_color}33 !important;
}}

.stButton > button:hover {{
    transform: scale(1.02);
    box-shadow: 0 6px 20px {accent_color}55 !important;
}}

.expense-red {{ color: #FF4B4B !important; font-weight: 600; }}
.income-green {{ color: #10B981 !important; font-weight: 600; }}

/* Scrollbar */
::-webkit-scrollbar {{
    width: 6px;
    height: 6px;
}}
::-webkit-scrollbar-track {{
    background: transparent;
}}
::-webkit-scrollbar-thumb {{
    background: {card_border};
    border-radius: 10px;
}}
::-webkit-scrollbar-thumb:hover {{
    background: {sub_text};
}}
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE INIT ---
if 'data' not in st.session_state: st.session_state.data = None
if 'categorizer' not in st.session_state: 
    st.session_state.categorizer = ExpenseCategorizer()
    st.session_state.categorizer.load_model() # Try to load existing model
if 'goal_manager' not in st.session_state: st.session_state.goal_manager = GoalManager()
if 'currency' not in st.session_state: st.session_state.currency = 'INR'

# Default profile values
if 'salary' not in st.session_state: st.session_state.salary = 5000.0
if 'stocks_inv' not in st.session_state: st.session_state.stocks_inv = 0.0
if 'bonds_inv' not in st.session_state: st.session_state.bonds_inv = 0.0
if 'commodities_inv' not in st.session_state: st.session_state.commodities_inv = 0.0

# Business Finance session state
if 'business_categorizer' not in st.session_state:
    st.session_state.business_categorizer = BusinessExpenseCategorizer()
if 'business_data' not in st.session_state:
    st.session_state.business_data = None

# Loan Calculator session state
if 'loans' not in st.session_state:
    st.session_state.loans = []

categorizer = st.session_state.categorizer
goal_manager = st.session_state.goal_manager
currency_symbol = st.session_state.currency # simplified symbol logic for now, or use map

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'app_mode' not in st.session_state:
    st.session_state.app_mode = None

# --- AUTHENTICATION UI ---
if not st.session_state.authenticated:
    st.markdown(f"<h1 style='text-align: center; color: {accent_color};'>💰 ExpenseTracker</h1>", unsafe_allow_html=True)
    
    st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] { gap: 20px; justify-content: center; }
    .stTabs [data-baseweb="tab"] {
        height: 50px; background-color: rgba(255, 255, 255, 0.05);
        border-radius: 10px 10px 0 0; padding: 10px 30px;
    }
    </style>
    """, unsafe_allow_html=True)

    tab_login, tab_signup = st.tabs(["🔐 Login", "📝 Sign Up"])
    
    with tab_login:
        st.subheader("Welcome Back")
        with st.form("Login"):
            user = st.text_input("Username")
            pw = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", use_container_width=True)
            if submitted:
                success, msg = login_user(user, pw)
                if success:
                    st.session_state.authenticated = True
                    st.session_state.username = user
                    st.rerun()
                else:
                    st.error(msg)
                    
    with tab_signup:
        st.subheader("Create an Account")
        with st.form("Sign Up"):
            new_user = st.text_input("Choose Username")
            new_pw = st.text_input("Choose Password", type="password")
            confirm_pw = st.text_input("Confirm Password", type="password")
            submitted = st.form_submit_button("Sign Up", use_container_width=True)
            if submitted:
                if new_pw != confirm_pw: st.error("Passwords do not match.")
                elif len(new_pw) < 4: st.error("Password must be at least 4 characters.")
                else:
                    success, msg = signup_user(new_user, new_pw)
                    if success: st.success(msg)
                    else: st.error(msg)
    st.stop()

# --- MODE SELECTION UI ---
if st.session_state.app_mode is None:
    st.markdown(f"<h2 style='text-align: center;'>Welcome, {st.session_state.username}</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; opacity: 0.8;'>Please select your finance mode for this session.</p>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="advisor-card" style="height: 320px !important; border-top: 6px solid {accent_color}; text-align: center;">
            <div style="font-size: 4rem; margin-bottom: 20px;">🏠</div>
            <h3>Individual</h3>
            <p>Manage personal expenses, savings, investments, and more.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Select Individual", key="mode_ind", use_container_width=True):
            st.session_state.app_mode = "Individual"
            st.rerun()
            
    with col2:
        st.markdown(f"""
        <div class="advisor-card" style="height: 320px !important; border-top: 6px solid #F472B6; text-align: center;">
            <div style="font-size: 4rem; margin-bottom: 20px;">🏢</div>
            <h3>Business</h3>
            <p>Track business revenue, high-volume expenses, and vendor metrics.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Select Business", key="mode_bus", use_container_width=True):
            st.session_state.app_mode = "Business"
            st.rerun()
            
    st.stop()

# Sidebar Header & Persistence
st.sidebar.title("💰 ExpenseTracker")
st.sidebar.markdown(f"**Welcome, <span class='username-color-span'>{st.session_state.username}</span>**", unsafe_allow_html=True)
st.sidebar.markdown(f"Mode: **{st.session_state.app_mode}**")

col_side1, col_side2 = st.sidebar.columns(2)
if col_side1.button("Logout", key="logout_btn", use_container_width=True):
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.app_mode = None # Clear mode on logout
    st.rerun()

if col_side2.button("Switch Mode", key="switch_mode_btn", use_container_width=True):
    st.session_state.app_mode = None
    st.rerun()

# Helper for navigation callback
def navigate_to(page_name):
    st.session_state.page = page_name

# Filtered Page List
if st.session_state.app_mode == "Individual":
    nav_options = ["📊 Dashboard", "🧠 Smart Advisor", "🔍 Analysis", "🎯 Budget & Goals", "📋 Transactions", "🏦 Loan Calculator", "⚙️ Settings"]
else: # Business
    nav_options = ["🏢 Business Finance", "⚙️ Settings"]

# Safety: Ensure current page is valid for the mode
if "page" not in st.session_state or st.session_state.page not in nav_options:
    st.session_state.page = nav_options[0]

page = st.sidebar.radio(
    "Navigation", 
    nav_options, 
    label_visibility="collapsed",
    key="page"
)

st.sidebar.markdown("---")
st.sidebar.info(f"✨ **Quote:**\n\n{get_random_quote()}")

# --- DATA PREP ---
df = st.session_state.get('data', None)
income_cats = ['Income', 'Salary', 'Deposit']

if df is not None:
    # Ensure standard cols
    if 'amount' in df.columns and df['amount'].dtype == 'object':
         df['amount'] = df['amount'].replace(r'[\$,]', '', regex=True)
         df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
    
    # Currency conversion for display
    curr = st.session_state.currency
    
    # Calculate totals
    mask_income = df['category'].isin(income_cats)
    total_income_native = df[mask_income]['amount'].sum()
    total_expense_native = df[~mask_income]['amount'].sum() # amounts are usually negative in bank stmts? 
    # Logic check: In current system, expenses are usually negative? 
    # Actually current dummy data has positive expenses. Let's stick to: Income is Income Category, Expense is everything else stats.
    # We will treat Expense sum as absolute for display.
    
    total_expense_abs = df[~mask_income]['amount'].abs().sum()
    total_balance_native = total_income_native - total_expense_abs
    
    # Convert
    total_income_disp = convert_amount(total_income_native, curr)
    total_expense_disp = convert_amount(total_expense_abs, curr)
    total_balance_disp = convert_amount(total_balance_native, curr)

# --- PAGES ---

if page == "📊 Dashboard":
    # Dynamic Greeting (Humane addition)
    hour = datetime.now().hour
    if 5 <= hour < 12: greeting = "Good Morning"
    elif 12 <= hour < 17: greeting = "Good Afternoon"
    else: greeting = "Good Evening"
    
    st.title(f"{greeting}, {st.session_state.username}!")
    
    if df is None:
        st.info("Please go to 'Settings' to upload your data.")
        st.stop()

    # Dashboard Story Summary
    breakdown = FinancialAdvisor(df, st.session_state.salary).analyze_50_30_20()
    savings_rate = breakdown['Savings']['pct'] if breakdown else 0
    top_cat = df[~df['category'].isin(income_cats)].groupby('category')['amount'].sum().abs().idxmax()
    
    st.markdown(f"""
    <div style="background: {card_bg}; border: 1px solid {card_border}; border-radius: 20px; padding: 25px; margin-bottom: 30px; border-left: 6px solid {accent_color};">
        <h3 style="margin:0; font-size:1.4rem; color:{text_color}; font-family: 'Plus Jakarta Sans', sans-serif;">Your Monthly Story</h3>
        <p style="font-size:1.1rem; color:{sub_text}; line-height:1.6; margin-top:10px; font-family: 'Inter', sans-serif;">
            This month, you've spent <b>{total_expense_disp}</b> with a focus on <b>{top_cat}</b>. 
            You're currently saving <b>{savings_rate:.1f}%</b> of your income — a humane approach to wealth building. 
            Check your insights below to refine your journey.
        </p>
    </div>
    """, unsafe_allow_html=True)
        
    # --- SMART ADVISOR INSIGHTS (Top 3) ---
    advisor = FinancialAdvisor(df, st.session_state.salary)
    insights = advisor.get_combined_insights()
    
    if insights:
        st.markdown("### ⚡ Actionable Insights")
        cols = st.columns(3)
        for i, insight in enumerate(insights[:3]): # Show top 3
            color_map = {"success": "#10B981", "warning": "#F59E0B", "alert": "#EF4444", "info": "#3B82F6"}
            b_color = color_map.get(insight['type'], "#64748B")
            icon = "✅" if insight['type'] == 'success' else "⚠️" if insight['type'] == 'warning' else "🚨" if insight['type'] == 'alert' else "ℹ️"
            
            with cols[i]:
                st.markdown(f"""
                <div class="advisor-card" style="border-left: 5px solid {b_color};">
                    <div>
                        <div style="display:flex; align-items:center; gap:10px; margin-bottom:10px;">
                            <span style="font-size:1.5rem;">{icon}</span>
                            <h4 style="margin:0; font-size:1.05rem; color:{text_color}; font-weight:700;">{insight['title']}</h4>
                        </div>
                        <div style="font-size:0.95rem; opacity:0.9; margin-bottom:10px; line-height:1.4;">
                            {insight['text']}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                # target logic
                target = "📊 Dashboard"
                act_text = str(insight['action'])
                if "Cutting Expenses" in act_text or "Anomalies" in act_text or "Rent/Utilities" in act_text: target = "🔍 Analysis"
                elif "Dining" in act_text or "Habit" in act_text or "essential" in act_text or "details" in act_text: target = "🎯 Budget & Goals"
                elif "Investing" in act_text: target = "🔍 Analysis"
                st.button(insight['action'], key=f"dash_adv_{i}", use_container_width=True, on_click=navigate_to, args=(target,))

        st.markdown("---")

    # Metrics
    # Calculate Forecast
    forecast = generate_spending_forecast(df, st.session_state.salary)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Balance", format_currency(total_balance_disp, curr))
    col2.metric("Total Income", format_currency(total_income_disp, curr))
    col3.metric("Total Expenses", format_currency(total_expense_disp, curr), delta_color="inverse")
    
    if forecast:
        proj_bal = convert_amount(forecast['projected_balance'], curr)
        col4.metric(f"Projected End-{forecast['month_name']}", format_currency(proj_bal, curr))
    else:
        col4.metric("Projected Balance", "N/A")
    
    st.markdown("---")
    
    col_main_left, col_main_right = st.columns([2, 1])
    
    with col_main_left:
        st.subheader("Recent Transactions")
        recent_txns = df.tail(5).iloc[::-1]
        
        for _, row in recent_txns.iterrows():
            cat = row.get('category', 'Unknown')
            desc = row.get('description', 'Transaction')
            amt_native = row.get('amount', 0)
            amt_disp = convert_amount(amt_native, curr)
            
            is_inc = cat in income_cats
            color_class = "income-green" if is_inc else "expense-red"
            sign = "+" if is_inc else "-"
            # Abs for display if sign is manual
            display_val = abs(amt_disp)
            
            icon = "💰" if is_inc else "❓"
            cat_lower = str(cat).lower()
            if 'shopping' in cat_lower: icon = "🛍"
            elif 'food' in cat_lower or 'dining' in cat_lower: icon = "🍔"
            elif 'transport' in cat_lower: icon = "🚗"
            elif 'health' in cat_lower: icon = "💊"
            elif 'utilities' in cat_lower: icon = "💡"
            elif 'entertainment' in cat_lower: icon = "🎬"
            elif 'housing' in cat_lower or 'rent' in cat_lower: icon = "🏠"
            elif 'travel' in cat_lower: icon = "✨"
            elif 'services' in cat_lower or 'insurance' in cat_lower: icon = "📋"
            
            st.markdown(f"""
            <div class="transaction-box">
                <div style="display:flex; align-items:center;">
                    <div class="transaction-icon">{icon}</div>
                    <div class="transaction-details">
                        <div style="font-weight:bold;">{cat}</div>
                        <div style="font-size:0.8em; opacity: 0.7;">{desc}</div>
                    </div>
                </div>
                <div class="transaction-amount {color_class}">
                    {sign} {format_currency(display_val, curr)}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        # Trends
        st.markdown("### 📈 Financial Trends")
        if 'date' in df.columns:
            try:
                df['date'] = pd.to_datetime(df['date'])
                
                # Prepare Dataframes
                # 1. Spending
                daily_spend = df[~mask_income].groupby('date')['amount'].sum().abs()
                
                # 2. Income
                daily_income = df[mask_income].groupby('date')['amount'].sum()
                
                # 3. Balance
                # For balance we need chronological running total
                # We need all transactions sorted by date
                df_sorted = df.sort_values('date')
                # Calculate signed amount (Income is +, Expense is -)
                # Ensure expense rows are negative if they aren't already
                # (In our logic above, we treated expenses as absolute for display, but here we need net flow)
                # Let's assume input data 'amount' is mixed sign or we need to enforce it based on category
                
                # Safe approach: 
                # If category is income, amount is +
                # If category is expense, amount is -
                df_sorted['net_amount'] = df_sorted.apply(
                    lambda x: abs(x['amount']) if x['category'] in income_cats else 0 - abs(x['amount']), axis=1
                )
                
                # Cumulative Sum
                df_sorted['running_balance'] = df_sorted['net_amount'].cumsum()
                # Group by date to get end-of-day balance
                daily_balance = df_sorted.groupby('date')['running_balance'].last()

                # TABS
                tab_spend, tab_inc, tab_bal = st.tabs(["💸 Spending", "💰 Income", "🏦 Balance"])
                
                with tab_spend:
                    st.caption("Daily Spending Trend")
                    st.line_chart(daily_spend, color="#FF4B4B")
                    
                with tab_inc:
                    st.caption("Daily Income Trend")
                    if not daily_income.empty:
                        st.line_chart(daily_income, color="#28a745")
                    else:
                        st.info("No income data to show trend.")
                        
                with tab_bal:
                    st.caption("Net Balance Growth")
                    st.line_chart(daily_balance, color="#007bff")
                    
            except Exception as e:
                st.warning(f"Trend visualization failed: {e}")

        # --- EXPORT SECTION ---
        st.markdown("### 💸 Export Reports")
        col_ex, col_pdf = st.columns(2)
        
        with col_ex:
            if st.button("Generate Excel Report 📊", use_container_width=True):
                excel_data = generate_excel(df)
                st.download_button(
                    label="Download Excel Now",
                    data=excel_data,
                    file_name=f"expense_tracker_{st.session_state.username}_{pd.Timestamp.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            
        with col_pdf:
            if st.button("Generate PDF Report 📄", use_container_width=True):
                try:
                    # Calculate Health Details for PDF
                    # Reusing logic from Achievements section
                    act_inc = df[mask_income]['amount'].sum()
                    fin_inc = act_inc if act_inc > 0 else st.session_state.get('salary', 50000)
                    tot_exp = df[~mask_income]['amount'].abs().sum()
                    invs = {
                        'stocks': st.session_state.get('stocks_inv', 0),
                        'bonds': st.session_state.get('bonds_inv', 0),
                        'commodities': st.session_state.get('commodities_inv', 0)
                    }
                    weights = {'savings':0.5, 'volume':0.3, 'allocation':0.2}
                    _, h_details = calculate_financial_health_score(fin_inc, tot_exp, invs, weights)

                    pdf_data = generate_pdf(df, curr, h_details)
                    st.download_button(
                        label="Download PDF Now",
                        data=pdf_data,
                        file_name=f"expense_report_{st.session_state.username}_{pd.Timestamp.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"PDF Generation Failed: {e}")

    with col_main_right:
        st.subheader("Overview")
        # Donut
        expense_df = df[~mask_income]
        if not expense_df.empty:
            cat_sum = expense_df.groupby('category')['amount'].sum().abs().reset_index()
            fig = px.pie(cat_sum, values='amount', names='category', hole=0.6, 
                         color_discrete_sequence=px.colors.qualitative.Prism)
            fig.update_layout(showlegend=False, margin={'t':0, 'b':0, 'l':0, 'r':0},
                              annotations=[{'text':"Exp", 'x':0.5, 'y':0.5, 'font_size':20, 'showarrow':False}])
            st.plotly_chart(fig, use_container_width=True)
            
        # --- BADGES ---
        st.subheader("Achievements")
        # Get score details for badges
        # We need to run health calc to get details
        # Reuse existing logic or call it here
        # Quick calc
        act_inc = df[mask_income]['amount'].sum()
        fin_inc = act_inc if act_inc > 0 else st.session_state.salary
        tot_exp = df[~mask_income]['amount'].abs().sum()
        # Mock investments for badge check
        invs = {'stocks':0, 'bonds':0, 'commodities':0} 
        weights = {'savings':0.5, 'volume':0.3, 'allocation':0.2}
        
        _, h_details = calculate_financial_health_score(fin_inc, tot_exp, invs, weights)
        
        badge_mgr = BadgeManager()
        badges = badge_mgr.check_badges(df, h_details)
        
        if badges:
            for b in badges:
                st.markdown(f"""
                <div style="background-color: rgba(255,215,0,0.1); border: 1px solid #FFD700; border-radius: 10px; padding: 10px; margin-bottom: 5px; display: flex; align-items: center;">
                    <div style="font-size: 24px; margin-right: 10px;">{b['icon']}</div>
                    <div>
                        <div style="font-weight: bold; color: #FFD700;">{b['name']}</div>
                        <div style="font-size: 0.8em; opacity: 0.8;">{b['description']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
             st.info("No badges earned yet. Keep saving!")

elif page == "🧠 Smart Advisor":
    st.title("💡 Smart Financial Advisor")
    
    if df is None: st.warning("No Data"); st.stop()
    
    advisor = FinancialAdvisor(df, st.session_state.salary)
    breakdown = advisor.analyze_50_30_20()
    
    st.markdown("### 📊 50/30/20 Rule Analysis")
    st.caption("The 50/30/20 rule recommends spending 50% on Needs, 30% on Wants, and saving 20%.")
    
    if breakdown:
        col1, col2, col3 = st.columns(3)
        
        # Helper to render card
        def render_rule_card(col, title, data, color):
            pct = data['pct']
            target = data['target']
            diff = pct - target
            
            with col:
                st.markdown(f"""
                <div class="advisor-card" style="border-left-color: {color};">
                    <h4 style="margin:0; color:{sub_text}">{title}</h4>
                    <h2 style="margin:0.2rem 0; font-size: 2.2rem;">{pct:.1f}%</h2>
                    <p style="opacity:0.7; font-size:0.9rem; margin-bottom: 0.5rem;">Target: {target}%</p>
                    <p style="font-weight:600; margin:0;">{format_currency(convert_amount(data['amount'], curr), curr)}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if abs(diff) > 5:
                    status = "⚠️ Off Track"
                    if (title == "Savings" and diff < 0) or (title != "Savings" and diff > 0):
                        st.error(f"{status} ({diff:+.1f}%)")
                    else:
                        st.success("✅ Good Buffer")
                else:
                    st.success("✅ On Track")

        render_rule_card(col1, "Needs", breakdown['Needs'], "#3498db")
        render_rule_card(col2, "Wants", breakdown['Wants'], "#e74c3c")
        render_rule_card(col3, "Savings", breakdown['Savings'], "#2ecc71")
        
        st.markdown("---")
        st.subheader("📝 Detailed Recommendations")
        
        # Use combined insights here too
        insights = advisor.get_combined_insights()
        
        # Grid-like layout for top 3 insights if possible, else list
        for i, insight in enumerate(insights):
            color_map = {"success": "#10B981", "warning": "#F59E0B", "alert": "#EF4444", "info": "#3B82F6"}
            border_color = color_map.get(insight['type'], "#64748B")
            icon = "✅" if insight['type'] == 'success' else "⚠️" if insight['type'] == 'warning' else "🚨" if insight['type'] == 'alert' else "ℹ️"
            
            st.markdown(f"""
            <div class="advisor-card" style="border-left: 5px solid {border_color};">
                <div>
                    <div style="display:flex; align-items:center; gap:10px; margin-bottom:10px;">
                        <span style="font-size:1.5rem;">{icon}</span>
                        <h4 style="margin:0; font-size:1.1rem; color:{text_color}; font-weight:700;">{insight['title']}</h4>
                    </div>
                    <div style="font-size:1rem; opacity:0.9; margin-bottom:15px; line-height:1.5;">
                        {insight['text']}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            target = "📊 Dashboard"
            act_text = str(insight['action'])
            if "Cutting Expenses" in act_text or "Anomalies" in act_text or "Rent/Utilities" in act_text: target = "🔍 Analysis"
            elif "Dining" in act_text or "Habit" in act_text or "essential" in act_text or "details" in act_text: target = "🎯 Budget & Goals"
            elif "Investing" in act_text: target = "🔍 Analysis" 
            
            # Button outside the card div to avoid styling conflicts
            st.button(insight['action'], key=f"adv_act_{i}", use_container_width=True, on_click=navigate_to, args=(target,))

elif page == "🔍 Analysis":
    st.title("Deep Dive Analysis")
    if df is None: st.warning("No data."); st.stop()
    assert df is not None
    
    t1, t2, t3 = st.tabs(["❤️ Financial Health", "⚠️ Anomalies", "🔄 Recurring"])
    
    with t1:
        st.subheader("Financial Health Score")
        # Profile Data (Now in Settings/Session)
        salary = st.session_state.salary
        invs = {'stocks': st.session_state.stocks_inv, 'bonds': st.session_state.bonds_inv, 'commodities': st.session_state.commodities_inv}
        
        # Scoring Weights (Interactive)
        with st.expander("⚙️ Scoring Weights", expanded=False):
            w_savings = st.slider("Savings", 0, 100, 50, 5)
            w_volume = st.slider("Volume", 0, 100, 30, 5)
            w_alloc = st.slider("Allocation", 0, 100, 20, 5)
            weights = {'savings': w_savings/100, 'volume': w_volume/100, 'allocation': w_alloc/100}

        # Calculate
        act_income = df[mask_income]['amount'].sum()
        final_income = act_income if act_income > 0 else salary
        total_exp_h = df[~mask_income]['amount'].abs().sum()
        
        score, details = calculate_financial_health_score(final_income, total_exp_h, invs, weights)
        
        c1, c2 = st.columns([1,3])
        c1.metric("Score", f"{score}/100")
        c2.progress(score/100)
        
        # Status badge
        if score < 50: st.warning("🚨 Your financial health needs attention.")
        elif score < 80: st.info("⚠️ You're doing okay, but there's room to improve.")
        else: st.success("🎉 Excellent financial health! Keep it up!")
        
        st.markdown("---")
        
        # Detailed Insights
        st.subheader("📊 Breakdown")
        m1, m2, m3 = st.columns(3)
        m1.metric("💰 Savings", f"{details.get('savings_ratio', 0):.1f}%", 
                  delta=f"{details.get('savings_ratio', 0) - 20:.1f}% vs 20% target")
        m2.metric("📈 Invested", f"{details.get('investment_ratio', 0):.1f}%",
                  delta=f"{details.get('investment_ratio', 0) - 20:.1f}% vs 20% target")
        m3.metric("🏦 Net Savings", f"{details.get('net_savings', 0):,.0f}")
        
        # New Contextual Insights (Humane addition)
        st.markdown("#### 💡 Contextual Indicators")
        col_c1, col_c2 = st.columns(2)
        
        # 1. Runway (Burn Rate)
        monthly_exp = df[~mask_income]['amount'].abs().sum()
        cash_on_hand = st.session_state.get('cash_buffer', 50000) # Fallback or better logic?
        # Actually total_balance is a better proxy if we have cumulative data
        runway = total_balance_native / monthly_exp if monthly_exp > 0 else 0
        
        with col_c1:
            st.markdown(f"""
            <div class="advisor-card" style="height: auto !important; padding: 15px !important;">
                <p style="margin:0; opacity:0.7; font-size:0.85rem;">MONTHLY RUNWAY</p>
                <h3 style="margin:5px 0;">{runway:.1f} Months</h3>
                <p style="margin:0; font-size:0.9rem;">How long you can last without new income.</p>
            </div>
            """, unsafe_allow_html=True)
            
        # 2. Debt-to-Income (if loans exist)
        total_emi = sum(loan.get('emi', 0) for loan in st.session_state.get('loans', []))
        dti = (total_emi / final_income) * 100 if final_income > 0 else 0
        
        with col_c2:
            st.markdown(f"""
            <div class="advisor-card" style="height: auto !important; padding: 15px !important;">
                <p style="margin:0; opacity:0.7; font-size:0.85rem;">DEBT-TO-INCOME (DTI)</p>
                <h3 style="margin:5px 0;">{dti:.1f}%</h3>
                <p style="margin:0; font-size:0.9rem;">Portion of income going to debt payments.</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Score breakdown
        sc1, sc2, sc3 = st.columns(3)
        sc1.caption(f"Savings Score: **{details.get('savings_score', 0)}** pts")
        sc2.caption(f"Volume Score: **{details.get('volume_score', 0)}** pts")
        sc3.caption(f"Allocation Score: **{details.get('allocation_score', 0)}** pts")
        
        # Investment Allocation
        st.markdown("---")
        st.subheader("📈 Investment Allocation")
        alloc = details.get('allocation', {'stocks': 0, 'bonds': 0, 'commodities': 0})
        total_inv = details.get('total_invested', 0)
        
        if total_inv > 0:
            ac1, ac2 = st.columns([1, 1])
            with ac1:
                st.markdown("**Your Allocation:**")
                st.write(f"📈 Stocks: **{alloc.get('stocks', 0):.1f}%**")
                st.write(f"📜 Bonds: **{alloc.get('bonds', 0):.1f}%**")
                st.write(f"📦 Commodities: **{alloc.get('commodities', 0):.1f}%**")
            with ac2:
                st.markdown("**Ideal Allocation (Target):**")
                st.write(f"📈 Stocks: **60%**")
                st.write(f"📜 Bonds: **30%**")
                st.write(f"📦 Commodities: **10%**")
        else:
            st.info("No investments recorded yet. Add them in Settings to get allocation insights.")
        
        # Investment Suggestions
        st.markdown("---")
        st.subheader("💡 Investment Suggestions")
        
        # Centralized advisor logic
        advisor = FinancialAdvisor(df, salary)
        suggestions = advisor.get_investment_suggestions(details, score)
        
        # Render as modern Action Cards
        for i, s in enumerate(suggestions):
            st.markdown(f"""
            <div style="background: {card_bg}; border: 1px solid {card_border}; border-radius: 12px; padding: 20px; margin-bottom: 20px; transition: all 0.3s ease; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                <div style="display:flex; align-items:center; gap:12px; margin-bottom:12px;">
                    <div style="font-size:2rem; background: rgba(79, 70, 229, 0.1); width: 50px; height: 50px; border-radius: 10px; display:flex; align-items:center; justify-content:center;">
                        {s['icon']}
                    </div>
                    <div style="font-weight:700; font-size:1.15rem; color:{text_color};">
                        {s['title']}
                    </div>
                </div>
                <div style="color:{sub_text}; line-height:1.6; font-size:1rem; margin-bottom:5px;">
                    {s['desc']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
    with t2:
        st.subheader("Anomaly Detection")
        # Ensure anomalies are checked
        if 'is_anomaly' not in df.columns:
            ad = AnomalyDetector()
            df = ad.detect_anomalies(df)
            st.session_state.data = df
            
        anomalies = df[df['is_anomaly'] == -1]
        if not anomalies.empty:
            st.warning(f"Found {len(anomalies)} anomalies")
            cols_to_show = ['date', 'description', 'category', 'amount', 'anomaly_reason']
            display_anomalies = anomalies[[c for c in cols_to_show if c in df.columns]].copy()
            if 'amount' in display_anomalies.columns:
                display_anomalies['amount'] = display_anomalies['amount'].round(2)
            st.dataframe(display_anomalies, use_container_width=True)
        else:
            st.success("No anomalies found.")
            
    with t3:
        st.subheader("Recurring Subscriptions")
        sd = SubscriptionDetector()
        subs = sd.detect_subscriptions(df)
        if not subs.empty:
            st.dataframe(subs, use_container_width=True)
        else:
            st.info("No subscriptions detected.")


elif page == "🎯 Budget & Goals":
    st.title("Budget & Goals")
    if df is None: st.warning("No Data"); st.stop()
    assert df is not None
    
    col_goals, col_budgets = st.columns(2)
    
    with col_goals:
        st.subheader("🎯 Goals")
        # Add Goal
        with st.form("new_goal"):
            name = st.text_input("Goal Name")
            target = st.number_input("Target Amount", value=1000.0)
            saved = st.number_input("Saved", value=0.0)
            date = st.date_input("Target Date")
            if st.form_submit_button("Add"):
                goal_manager.add_goal(name, target, saved, date)
                st.rerun()
        
        # List Goals
        goals_df = goal_manager.get_goals()
        if not goals_df.empty:
            for i, row in goals_df.iterrows():
                with st.container():
                    col_g_info, col_g_del = st.columns([4, 1])
                    with col_g_info:
                        st.write(f"**{row['name']}**")
                        st.progress(min(row['saved_amount']/row['target_amount'], 1.0))
                        st.caption(f"{row['saved_amount']} / {row['target_amount']}")
                    with col_g_del:
                        st.write("") # Adjust spacing
                        if st.button("🗑", key=f"goal_del_{i}"):
                            goal_manager.delete_goal(i)
                            st.rerun()
                    st.divider()
    
    with col_budgets:
        st.subheader("💰 Budgets")
        if 'budgets' not in st.session_state: st.session_state.budgets = {}
        
        cats = sorted(df[~mask_income]['category'].unique())
        s_cat = st.selectbox("Category", cats)
        lim = st.number_input("Limit", value=0.0, step=50.0)
        if st.button("Set Budget"):
            st.session_state.budgets[s_cat] = lim
            st.success(f"Set {s_cat} to {lim}")
            
        # Track
        # Fix: sum() first then abs(), or abs() before groupby
        # Let's do sum().abs() to get total spent magnitude
        act_spend = df[~mask_income].groupby('category')['amount'].sum().abs()
        
        st.write("---")
        for cat, limit in st.session_state.budgets.items():
            spent = df[df['category']==cat]['amount'].abs().sum()
            st.write(f"**{cat}**: {spent:,.2f} / {limit:,.2f}")
            if limit > 0:
                st.progress(min(spent/limit, 1.0))


elif page == "📋 Transactions":
    st.title("Transactions")
    if df is None: st.warning("No Data"); st.stop()
    assert df is not None
    
    edited = st.data_editor(df, num_rows="dynamic", key="main_editor", use_container_width=True)
    if st.button("Save Changes & Retrain"):
        categorizer.train(edited)
        st.session_state.data = edited
        st.success("Updated!")
        st.rerun()


elif page == "🏢 Business Finance":
    st.title("🏢 Business Finance & GST Manager")

    # --- Helper: Indian Currency Formatting ---
    def format_indian_currency(value):
        try:
            val = float(value)
        except:
            return value
        if abs(val) >= 10000000:
            return f"₹{val/10000000:.2f} Cr"
        elif abs(val) >= 100000:
            return f"₹{val/100000:.2f} L"
        else:
            return f"₹{val:,.2f}"

    # --- Data Loading (from session state, uploaded via Settings) ---
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🏢 Business Settings")
    tax_bracket = st.sidebar.selectbox("Corporate Tax Bracket", options=[15, 22, 25, 30, 0], format_func=lambda x: f"{x}%", help="Select applicable income tax rate")
    tax_rate = tax_bracket / 100.0

    biz_categorizer = st.session_state.business_categorizer

    if st.session_state.business_data is None:
        st.info("No business data loaded. Go to **⚙️ Settings** to upload a Business CSV.")
        st.stop()
    else:
        # Only proceed if we have data
        biz_df = st.session_state.business_data.copy()

        # Date Filter
        if biz_df is not None and not biz_df.empty:
            biz_min_date = biz_df['date'].min().date()
            biz_max_date = biz_df['date'].max().date()
            biz_start = st.sidebar.date_input("Start Date", biz_min_date, key="biz_start")
            biz_end = st.sidebar.date_input("End Date", biz_max_date, key="biz_end")
            
            mask = (biz_df['date'].dt.date >= biz_start) & (biz_df['date'].dt.date <= biz_end)
            biz_filtered = biz_df.loc[mask]
    
            # PDF Report
            st.sidebar.markdown("### 📄 Reports")
            biz_df['fiscal_year'] = biz_df['date'].apply(lambda x: x.year + 1 if x.month >= 4 else x.year)
            available_years = sorted(biz_df['fiscal_year'].unique(), reverse=True)
            selected_years_report = st.sidebar.multiselect("Select Years for Report", available_years, default=available_years[:1])
            
            if st.sidebar.button("Generate Business PDF"):
                from src.pdf_generator import generate_pdf_report  # type: ignore
                with st.spinner("Generating PDF..."):
                    pdf = generate_pdf_report(biz_df, selected_years_report, tax_rate)
                    pdf_output = pdf.output(dest='S')
                    # Safety check for fpdf2 output type
                    if isinstance(pdf_output, str):
                        pdf_output = pdf_output.encode('latin-1')
                    
                    st.sidebar.download_button(
                        label="⬇️ Download PDF",
                        data=pdf_output,
                        file_name=f"Business_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf"
                    )
    
            # --- Tabs ---
            biz_tab1, biz_tab2, biz_tab3, biz_tab4 = st.tabs(["📊 Dashboard", "📝 GST Analysis", "❤️ Financial Health", "📂 Data"])
    
            # --- TAB 1: Dashboard ---
            with biz_tab1:
                st.header("Business Overview")
    
                # Current FY Snapshot
                max_d = biz_df['date'].max()
                current_fy = max_d.year + 1 if max_d.month >= 4 else max_d.year
                fy_start = pd.Timestamp(f"{current_fy-1}-04-01")
                fy_end_ts = pd.Timestamp(f"{current_fy}-03-31")
                current_fy_df = biz_df[(biz_df['date'] >= fy_start) & (biz_df['date'] <= fy_end_ts)]
    
                if not current_fy_df.empty:
                    st.subheader(f"📅 Current Financial Year (FY{current_fy}) Snapshot")
                    cy_rev = current_fy_df[current_fy_df['amount'] > 0]['amount'].sum()
                    cy_exp = current_fy_df[current_fy_df['amount'] < 0]['amount'].sum()
                    cy_profit = cy_rev + cy_exp
                    cy_tax = max(0, cy_profit * tax_rate)
                    cy_pat = cy_profit - cy_tax
                    cy_gst_net = current_fy_df[current_fy_df['amount'] > 0]['gst_amount'].sum() - current_fy_df[current_fy_df['amount'] < 0]['gst_amount'].sum()
                    if cy_profit < 0: cy_gst_net = 0
    
                    m1, m2, m3, m4, m5 = st.columns(5)
                    m1.metric("FY Revenue", format_indian_currency(cy_rev))
                    m2.metric("FY Expenses", format_indian_currency(abs(cy_exp)))
                    m3.metric("FY Profit (Pre-Tax)", format_indian_currency(cy_profit))
                    m4.metric("FY Tax", format_indian_currency(cy_tax))
                    m5.metric("FY Profit (Post-Tax)", format_indian_currency(cy_pat))
                    st.divider()
    
                st.subheader("Selected Period Overview")
                total_revenue = biz_filtered[biz_filtered['amount'] > 0]['amount'].sum()
                total_expenses = biz_filtered[biz_filtered['amount'] < 0]['amount'].sum()
                net_profit = total_revenue + total_expenses
                gst_collected = biz_filtered[biz_filtered['amount'] > 0]['gst_amount'].sum()
                gst_paid = biz_filtered[biz_filtered['amount'] < 0]['gst_amount'].sum()
                net_gst_payable = gst_collected - gst_paid
                if net_profit < 0: net_gst_payable = 0
                income_tax = max(0, net_profit * tax_rate)
                net_profit_post_tax = net_profit - income_tax
    
                st.markdown("### Key Metrics")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Total Revenue", format_indian_currency(total_revenue))
                c2.metric("Total Expenses", format_indian_currency(abs(total_expenses)))
                c3.metric("Net Profit (Pre-Tax)", format_indian_currency(net_profit))
                c4.metric("Net GST Payable", format_indian_currency(net_gst_payable))
                c5, c6 = st.columns(2)
                c5.metric("Income Tax Payable", format_indian_currency(income_tax), help=f"Calculated at {tax_bracket}% on Net Profit")
                c6.metric("Net Profit (Post-Tax)", format_indian_currency(net_profit_post_tax))
    
                # Charts
                c_chart1, c_chart2 = st.columns(2)
                with c_chart1:
                    st.subheader("Income vs Expenses")
                    df_chart = biz_filtered.copy()
                    df_chart['month'] = df_chart['date'].dt.strftime('%Y-%m')
                    df_chart['type'] = df_chart['amount'].apply(lambda x: 'Income' if x > 0 else 'Expense')
                    df_chart['abs_amount'] = df_chart['amount'].abs()
                    chart = alt.Chart(df_chart).mark_bar().encode(
                        x='month', y='sum(abs_amount)', color='type',
                        tooltip=['month', 'type', 'sum(abs_amount)']
                    ).properties(title="Monthly Trends")
                    st.altair_chart(chart, use_container_width=True)
    
                with c_chart2:
                    st.subheader("Expenses by Category")
                    expense_biz = biz_filtered[biz_filtered['amount'] < 0].copy()
                    expense_biz['abs_amount'] = expense_biz['amount'].abs()
                    pie = alt.Chart(expense_biz).mark_arc().encode(
                        theta=alt.Theta("sum(abs_amount)", stack=True),
                        color=alt.Color("category"),
                        tooltip=["category", alt.Tooltip("sum(abs_amount)", format=",")]
                    ).properties(title="Expense Breakdown")
                    st.altair_chart(pie, use_container_width=True)
    
            # --- TAB 2: GST Analysis ---
            with biz_tab2:
                st.header("GST Analysis & Filing Helper")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("### 💸 Input Tax Credit (ITC)")
                    st.metric("Total GST Paid on Expenses", f"₹{gst_paid:,.2f}")
                    st.caption("Tax you paid on purchases/expenses. You can claim this back.")
                with col2:
                    st.markdown("### 🧾 Output GST Liability")
                    st.metric("Total GST Collected on Sales", f"₹{gst_collected:,.2f}")
                    st.caption("Tax collected from clients. You owe this to the govt.")
                st.divider()
                st.subheader("Net Position")
                if net_gst_payable > 0:
                    st.error(f"You need to pay ₹{net_gst_payable:,.2f} to the Government.")
                else:
                    st.success(f"You have a GST Credit of ₹{abs(net_gst_payable):,.2f} to carry forward.")
                st.subheader("Transaction-wise GST Details")
                gst_table = biz_filtered[['date', 'description', 'category', 'amount', 'gst_rate', 'gst_amount']].copy()
                gst_table['type'] = gst_table['amount'].apply(lambda x: 'Sale' if x > 0 else 'Purchase')
                st.dataframe(gst_table, use_container_width=True)
    
            # --- TAB 3: Financial Health ---
            with biz_tab3:
                st.header("Business Health Score")
                if total_revenue > 0:
                    margin = (net_profit / total_revenue) * 100
                else:
                    margin = 0
                num_months = (biz_filtered['date'].max() - biz_filtered['date'].min()).days / 30
                if num_months < 1: num_months = 1
                burn_rate = abs(total_expenses) / num_months
                st.metric("Net Profit Margin", f"{margin:.1f}%")
    
                biz_score = 0
                if margin > 30: biz_score += 40
                elif margin > 15: biz_score += 25
                elif margin > 0: biz_score += 10
                if net_profit > 0: biz_score += 30
                biz_score += 30  # compliance baseline
                st.progress(biz_score/100)
                st.write(f"**Business Health Score: {biz_score}/100**")
                if biz_score < 50:
                    st.warning("Profit margins are low. Review overhead costs.")
                else:
                    st.success("Business is healthy! Maintain sales velocity.")
    
                st.markdown("---")
                st.header("📈 5-Year Financial Trend")
                df_annual = biz_df.copy()
                df_annual['fiscal_year'] = df_annual['date'].apply(lambda x: x.year + 1 if x.month >= 4 else x.year)
                current_assets = 5000000.0
                current_liabilities = 2000000.0
                annual_stats = []
                years = sorted(df_annual['fiscal_year'].unique())
    
                for year in years:
                    fy_s = pd.Timestamp(f"{year-1}-04-01")
                    fy_e = pd.Timestamp(f"{year}-03-31")
                    year_data = df_annual[(df_annual['date'] >= fy_s) & (df_annual['date'] <= fy_e)]
                    if year_data.empty: continue
                    revenue = year_data[year_data['amount'] > 0]['amount'].sum()
                    expenses = year_data[year_data['amount'] < 0]['amount'].sum()
                    np_val = revenue + expenses
                    hist_tax = max(0, np_val * tax_rate)
                    pat = np_val - hist_tax
                    interest = year_data[year_data['category'] == 'Interest']['amount'].abs().sum()
                    depreciation = year_data[year_data['category'] == 'Depreciation']['amount'].abs().sum()
                    ebitda = np_val + interest + depreciation
                    current_assets += pat
                    current_liabilities = current_liabilities * 0.9
                    if pat < 0: current_liabilities += abs(pat)
                    annual_stats.append({
                        'Fiscal Year': f"FY{year}", 'Revenue': revenue, 'Net Profit (Pre-Tax)': np_val,
                        'Income Tax': hist_tax, 'Net Profit (Post-Tax)': pat, 'EBITDA': ebitda,
                        'Assets': current_assets, 'Liabilities': current_liabilities
                    })
    
                stats_df = pd.DataFrame(annual_stats)
                if not stats_df.empty:
                    cols_to_calc = ['Revenue', 'Net Profit (Pre-Tax)', 'Net Profit (Post-Tax)', 'EBITDA', 'Assets', 'Liabilities']
                    for col in cols_to_calc:
                        stats_df[f'{col} Growth %'] = stats_df[col].pct_change() * 100
                    st.subheader("Annual Financial Metrics")
                    display_df = stats_df.copy()
                    for col in cols_to_calc:
                        display_df[col] = display_df[col].apply(lambda x: f"₹{x:,.2f}")
                        display_df[f'{col} Growth %'] = display_df[f'{col} Growth %'].apply(lambda x: f"{x:+.2f}%" if pd.notnull(x) else "-")
                    st.dataframe(display_df, use_container_width=True)
                    st.subheader("Trend Visualization")
                    metric_to_plot = st.selectbox("Select Metric", cols_to_calc)
                    chart = alt.Chart(stats_df).mark_line(point=True).encode(
                        x='Fiscal Year', y=metric_to_plot,
                        tooltip=['Fiscal Year', metric_to_plot, f'{metric_to_plot} Growth %']
                    ).properties(title=f"{metric_to_plot} over 5 Years")
                    st.altair_chart(chart, use_container_width=True)
    
            # --- TAB 4: Data ---
            with biz_tab4:
                st.header("Data Management")
                edited_biz = st.data_editor(biz_filtered, num_rows="dynamic", key="biz_editor")
                if st.button("Retrain Business Model"):
                    with st.spinner("Training..."):
                        try:
                            biz_categorizer.train(edited_biz)
                            st.success("Business model retrained!")
                        except Exception as e:
                            st.error(f"Training failed: {e}")
                st.download_button(
                    label="Download Processed Data",
                    data=edited_biz.to_csv(index=False).encode('utf-8'),
                    file_name='business_financial_data.csv', mime='text/csv'
                )


elif page == "🏦 Loan Calculator":
    st.title("🏦 Multi-Loan Debt Strategist")

    # --- Loan Calculation Functions ---
    def calculate_emi(principal, rate_annual, tenure_years):
        if rate_annual <= 0 or tenure_years <= 0: return 0
        r = rate_annual / (12 * 100)
        n = tenure_years * 12
        emi = principal * r * ((1 + r)**n) / (((1 + r)**n) - 1)
        return emi

    def get_outstanding_balance(principal, rate_annual, tenure_years, months_paid, total_prepayments=0):
        r = rate_annual / (12 * 100)
        n = tenure_years * 12
        emi = calculate_emi(principal, rate_annual, tenure_years)
        if months_paid == 0:
            theoretical_bal = principal
        else:
            term1 = principal * ((1 + r)**months_paid)
            term2 = (emi/r) * (((1+r)**months_paid) - 1)
            theoretical_bal = term1 - term2
        return max(0, theoretical_bal - total_prepayments)

    # --- Sidebar (Loan-specific) ---
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🏦 Loan Settings")
    monthly_income = st.sidebar.number_input("Monthly Income (Net)", min_value=0.0, value=80000.0, step=1000.0, key="loan_income")
    st.sidebar.info("💡 Only use cash *excess* of your Emergency Fund.")
    lumpsum_available = st.sidebar.number_input("One-time Cash for Debt", min_value=0.0, value=0.0, step=5000.0, key="loan_lumpsum")

    # --- Aggregate Calculations ---
    total_emi = 0
    total_outstanding = 0
    total_original_principal = 0
    loans_data = []
    max_tenure_months = 0

    for loan in st.session_state.loans:
        emi = calculate_emi(loan['p'], loan['r'], loan['n'])
        bal = get_outstanding_balance(loan['p'], loan['r'], loan['n'], loan['paid'], loan['extra_paid'])
        total_emi += emi
        total_outstanding += bal
        total_original_principal += loan['p']
        remaining_m = (loan['n'] * 12) - loan['paid']
        if remaining_m > max_tenure_months:
            max_tenure_months = remaining_m
        loans_data.append({'name': loan['name'], 'balance': bal, 'rate': loan['r'], 'emi': emi})

    total_future_interest = 0
    for loan in st.session_state.loans:
        if loan['p'] > 0 and loan['r'] > 0:
            r_mo = loan['r'] / 1200
            current_emi = calculate_emi(loan['p'], loan['r'], loan['n'])
            current_bal = get_outstanding_balance(loan['p'], loan['r'], loan['n'], loan['paid'], loan['extra_paid'])
            if current_bal > 0:
                try:
                    val = 1 - (r_mo * current_bal / current_emi)
                    if val > 0:
                        real_rem = -np.log(val) / np.log(1 + r_mo)
                        total_future_interest += (real_rem * current_emi) - current_bal
                except:
                    pass

    total_amount_payable = total_outstanding + total_future_interest
    payoff_year = date.today().year + int(max_tenure_months/12)

    # --- Tabs ---
    loan_tab1, loan_tab2, loan_tab3 = st.tabs(["📊 Dashboard & Schedule", "🧠 Smart Strategy", "🔄 Balance Transfer"])

    # --- TAB 1: Dashboard ---
    with loan_tab1:
        st.header("Loan Overview")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Monthly EMI", f"₹{total_emi:,.2f}")
        m2.metric("Total Interest (Future)", f"₹{total_future_interest:,.2f}")
        m3.metric("Total Outstanding", f"₹{total_amount_payable:,.2f}")
        m4.metric("Payoff Date", f"{payoff_year} (Approx)")
        st.markdown("---")

        c1, c2 = st.columns([2, 1])
        with c1:
            st.subheader("Amortization Curve")
            if not st.session_state.loans:
                st.info("Add a loan to see the curve.")
            else:
                months = range(1, int(max_tenure_months) + 1)
                agg_schedule = []
                current_balances = [l['balance'] for l in loans_data]
                current_emis = [l['emi'] for l in loans_data]
                current_rates = [l['rate']/1200 for l in loans_data]
                for m in months:
                    p_paid_month = 0; i_paid_month = 0
                    for i in range(len(current_balances)):
                        if current_balances[i] > 0:
                            interest = current_balances[i] * current_rates[i]
                            principal = current_emis[i] - interest
                            if principal > current_balances[i]:
                                principal = current_balances[i]; interest = 0
                            current_balances[i] -= principal
                            p_paid_month += principal; i_paid_month += interest
                    agg_schedule.append({"Month": m, "Principal Paid": p_paid_month, "Interest Paid": i_paid_month})
                    if sum(current_balances) <= 1: break

                chart_df = pd.DataFrame(agg_schedule)
                chart_melt = chart_df.melt('Month', var_name='Type', value_name='Amount')
                chart = alt.Chart(chart_melt).mark_area().encode(
                    x='Month', y='Amount',
                    color=alt.Color('Type', scale=alt.Scale(domain=['Interest Paid', 'Principal Paid'], range=['#1f77b4', '#aec7e8'])),
                    tooltip=['Month', 'Type', 'Amount']
                ).interactive()
                st.altair_chart(chart, use_container_width=True)

        with c2:
            st.subheader("Principal vs Interest")
            if total_outstanding > 0:
                pie_data = pd.DataFrame({'Category': ['Principal', 'Total Interest'], 'Amount': [total_outstanding, total_future_interest]})
                pie = alt.Chart(pie_data).mark_arc(innerRadius=60).encode(
                    theta='Amount',
                    color=alt.Color('Category', scale=alt.Scale(domain=['Principal', 'Total Interest'], range=['#1f77b4', '#aec7e8'])),
                    tooltip=['Category', 'Amount']
                )
                st.altair_chart(pie, use_container_width=True)
            else:
                st.caption("No outstanding debt.")

        # Loan Management
        with st.expander("📝 Manage Your Loans (Add / Remove)", expanded=False):
            col_add, col_list = st.columns([1, 2])
            with col_add:
                with st.form("add_loan_form"):
                    st.markdown("#### Add New Loan")
                    l_name = st.text_input("Name", value="Home Loan")
                    l_p = st.number_input("Principal (₹)", min_value=1000.0, value=500000.0, step=10000.0)
                    l_r = st.number_input("Annual Interest Rate (%)", min_value=0.1, value=8.5, step=0.1, format="%.2f")
                    l_n = st.number_input("Loan Tenure (Years)", min_value=0.5, value=20.0, step=0.5)
                    l_paid = st.number_input("Months Already Paid", min_value=0, value=0, step=1)
                    l_pre = st.number_input("Past Lump Sums Paid (₹)", min_value=0.0, value=0.0, step=1000.0)
                    if st.form_submit_button("Add Loan"):
                        st.session_state.loans.append({
                            'id': len(st.session_state.loans)+1,
                            'name': l_name, 'p': l_p, 'r': l_r, 'n': l_n, 'paid': l_paid, 'extra_paid': l_pre
                        })
                        st.rerun()
            with col_list:
                st.markdown("#### Active Loans")
                if not st.session_state.loans:
                    st.info("No loans found.")
                else:
                    for i, l in enumerate(st.session_state.loans):
                        cols = st.columns([2, 1, 1, 1])
                        cols[0].write(f"**{l['name']}**")
                        cols[1].write(f"₹{l['p']:,.0f}")
                        cols[2].write(f"{l['r']}%")
                        if cols[3].button("🗑", key=f"loan_del_{i}"):
                            st.session_state.loans.pop(i)
                            st.rerun()

    # --- TAB 2: Smart Strategy ---
    with loan_tab2:
        st.header("🧠 Smart Strategy")
        if monthly_income > 0:
            dti = (total_emi / monthly_income) * 100
            if dti > 20:
                st.error(f"🚨 **High Debt Burden**: EMI is {dti:.1f}% of Income (>20%).")
            else:
                st.success(f"✅ **Healthy Status**: EMI is {dti:.1f}% of Income.")
        st.divider()

        col_strat, col_res = st.columns(2)
        with col_strat:
            st.subheader("Payoff Strategy")
            strategy = st.radio("Choose Method", ["❄️ Snowball (Smallest Bal First)", "🌋 Avalanche (Highest Rate First)"])
            if st.session_state.loans:
                loans_copy = loans_data.copy()
                if "Snowball" in strategy:
                    sorted_loans = sorted(loans_copy, key=lambda x: x['balance'])
                else:
                    sorted_loans = sorted(loans_copy, key=lambda x: x['rate'], reverse=True)
                st.markdown("#### Suggested Priority Order")
                for idx, l in enumerate(sorted_loans):
                    st.write(f"{idx+1}. **{l['name']}** (Bal: ₹{l['balance']:,.0f}, Rate: {l['rate']}%)")

        with col_res:
            st.subheader("Lump Sum Allocator")
            st.caption(f"Based on Available Cash: ₹{lumpsum_available:,.0f}")
            if lumpsum_available > 0 and st.session_state.loans:
                rem_cash = lumpsum_available
                alloc_plan = []
                for l in sorted_loans:
                    if rem_cash <= 0: break
                    pay = min(rem_cash, l['balance'])
                    alloc_plan.append({'Loan': l['name'], 'Pay': f"₹{pay:,.0f}"})
                    rem_cash -= pay
                st.table(alloc_plan)
            elif not st.session_state.loans:
                st.info("Add loans to see allocation.")
            else:
                st.warning("Enter 'One-time Cash' in Sidebar to see allocation.")

    # --- TAB 3: Balance Transfer ---
    with loan_tab3:
        st.header("🔄 Balance Transfer Analysis")
        st.write("Compare your loans with a new offer.")
        if not st.session_state.loans:
            st.info("Add loans first.")
        else:
            loan_names = [l['name'] for l in st.session_state.loans]
            selected_loan_name = st.selectbox("Select Loan to Transfer", loan_names)
            selected_loan = next((l for l in st.session_state.loans if l['name'] == selected_loan_name), None)
            if selected_loan:
                cur_bal = get_outstanding_balance(selected_loan['p'], selected_loan['r'], selected_loan['n'], selected_loan['paid'], selected_loan['extra_paid'])
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("#### New Offer Details")
                    new_r = st.number_input("New Interest Rate (%)", 0.1, 20.0, 8.5, key="bt_rate")
                    proc_fee = st.number_input("Processing Fee (%)", 0.0, 5.0, 0.5, key="bt_fee")
                    other_cost = st.number_input("Fixed Costs", 0.0, 10000.0, 2000.0, key="bt_cost")
                with c2:
                    st.markdown("#### Comparison")
                    rem_months = max(0, (selected_loan['n'] * 12) - selected_loan['paid'])
                    if cur_bal > 0 and selected_loan['r'] > 0:
                        emi_old = calculate_emi(selected_loan['p'], selected_loan['r'], selected_loan['n'])
                        old_total_pay = emi_old * rem_months
                        old_int_rem = max(0, old_total_pay - cur_bal)
                        st.metric("Current Future Interest", f"₹{old_int_rem:,.0f}")

                        transfer_cost = (cur_bal * proc_fee / 100) + other_cost
                        new_principal = cur_bal + transfer_cost
                        new_n_years = rem_months / 12
                        if new_n_years < 0.1: new_n_years = 1.0
                        new_emi = calculate_emi(new_principal, new_r, new_n_years)
                        new_total_pay = new_emi * rem_months
                        new_int = new_total_pay - new_principal
                        st.metric("New Future Interest", f"₹{new_int:,.0f}")
                        st.caption(f"Includes Transfer Costs: ₹{transfer_cost:,.0f}")

                        final_savings = old_total_pay - new_total_pay
                        st.divider()
                        if final_savings > 0:
                            st.success(f"✅ **Switch & Save**: You will save **₹{final_savings:,.0f}** over the remaining tenure!")
                        else:
                            st.error(f"❌ **Don't Switch**: You will lose **₹{abs(final_savings):,.0f}**.")


elif page == "⚙️ Settings":
    st.title("Settings")
    
    if st.session_state.app_mode == "Individual":
        st.subheader("Data Upload")
        up_file = st.file_uploader("Upload Personal Expense CSV", type=['csv'])
        if up_file:
            try:
                raw = load_data(up_file)
                pro = preprocess_data(raw)
                cn = st.session_state.categorizer.predict(pro)
                ad = AnomalyDetector()
                fn = ad.detect_anomalies(cn)
                st.session_state.data = fn
                st.success("Personal expense data loaded!")
            except Exception as e:
                st.error(f"Error: {e}")

    if st.session_state.app_mode == "Business":
        st.subheader("Business Data Upload")
        biz_file = st.file_uploader("Upload Business Statement (CSV)", type=['csv'], key="biz_settings_upload")
        if biz_file:
            try:
                bdf = pd.read_csv(biz_file)
                bdf.columns = [c.lower().strip() for c in bdf.columns]
                if 'date' in bdf.columns:
                    bdf['date'] = pd.to_datetime(bdf['date'])
                bdf = preprocess_data(bdf)
                bdf = st.session_state.business_categorizer.predict(bdf)
                if 'gst_rate' not in bdf.columns:
                    bdf['gst_rate'] = 0.0
                if 'gst_amount' not in bdf.columns:
                    bdf['gst_amount'] = 0.0
                st.session_state.business_data = bdf
                st.success("Business data loaded! Go to Business Finance to view.")
            except Exception as e:
                st.error(f"Error loading business data: {e}")
            
    st.markdown("---")
    st.subheader("User Profile")
    st.session_state.salary = st.number_input("Monthly Salary", value=st.session_state.salary)
    
    c1, c2, c3 = st.columns(3)
    st.session_state.stocks_inv = c1.number_input("Stocks", value=st.session_state.stocks_inv)
    st.session_state.bonds_inv = c2.number_input("Bonds", value=st.session_state.bonds_inv)
    st.session_state.commodities_inv = c3.number_input("Commodities", value=st.session_state.commodities_inv)
    
    st.markdown("---")
    st.subheader("Preferences")
    cur_opts = ["USD", "EUR", "GBP", "INR", "JPY"]
    new_curr = st.selectbox("Currency", cur_opts, index=cur_opts.index(st.session_state.currency) if st.session_state.currency in cur_opts else 0)
    if new_curr != st.session_state.currency:
        st.session_state.currency = new_curr
        st.rerun()
        
    is_dark = st.session_state.theme == 'Dark'
    if st.toggle("Dark Mode", value=is_dark):
        st.session_state.theme = 'Dark'
    else:
        st.session_state.theme = 'Light'
        
    st.markdown("---")
    st.subheader("Advanced:")
    if st.button("🧠 Retrain Categorization Model"):
        if st.session_state.data is not None:
            with st.spinner("Training model on current data..."):
                st.session_state.categorizer.train(st.session_state.data)
            st.success("Model retrained and saved! Future transactions will be categorized better.")
        else:
            st.warning("No data to train on. Upload a CSV first.")
