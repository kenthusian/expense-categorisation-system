import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
import plotly.express as px  # type: ignore
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

# --- PAGE CONFIG ---
st.set_page_config(page_title="Expense Tracker", layout="wide", initial_sidebar_state="expanded")

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

st.markdown(f"""
<style>
/* Main Background */
.stApp {{
    background-color: {bg_color} !important;
    color: {text_color} !important;
}}
/* Text Color Override */
h1, h2, h3, h4, h5, h6, p, li, ol, ul, span, div.stMarkdown, label {{
    color: {text_color} !important;
}}
/* Cards */
div.css-1r6slb0.e1tzin5v2, div.stMetric, div[data-testid="stMetric"] {{
    background-color: {card_color} !important;
    border-radius: 15px;
    padding: 15px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    border: 1px solid {border_color};
    color: {text_color} !important;
}}
[data-testid="stMetricValue"] {{
    font-size: 2rem;
    font-weight: bold;
    color: {text_color} !important;
}}
[data-testid="stMetricLabel"] {{
    color: {text_color} !important;
    opacity: 0.8;
}}
/* Sidebar */
[data-testid="stSidebar"] {{
    background-color: {secondary_bg} !important;
    border-right: 1px solid {border_color};
}}
[data-testid="stSidebar"] * {{
    color: {text_color} !important;
}}
/* Transaction Box */
.transaction-box {{
    background-color: {card_color} !important;
    padding: 15px;
    border-radius: 15px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    margin-bottom: 10px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border: 1px solid {border_color};
    color: {text_color} !important;
}}
.transaction-icon {{
    font-size: 24px;
    margin-right: 15px;
    background-color: {icon_bg};
    padding: 10px;
    border-radius: 50%;
    color: #333 !important;
}}
.transaction-details div {{
    color: {text_color} !important;
}}
.transaction-amount {{
    font-weight: bold;
}}
.expense-red {{ color: #FF4B4B !important; }}
.income-green {{ color: #28a745 !important; }}
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

categorizer = st.session_state.categorizer
goal_manager = st.session_state.goal_manager
currency_symbol = st.session_state.currency # simplified symbol logic for now, or use map

# --- AUTHENTICATION STATE ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = None

# --- AUTHENTICATION UI ---
if not st.session_state.authenticated:
    st.title("💰 Expense Tracker")
    
    # Custom CSS for Auth
    st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.2rem;
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
                if new_pw != confirm_pw:
                    st.error("Passwords do not match.")
                elif len(new_pw) < 4:
                    st.error("Password must be at least 4 characters.")
                else:
                    success, msg = signup_user(new_user, new_pw)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)
    st.stop() # Stop rendering the rest of the app if not authenticated

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("💰 ExpenseTracker")
st.sidebar.markdown(f"**Welcome, {st.session_state.username}**")

if st.sidebar.button("Logout", key="logout_btn"):
    st.session_state.authenticated = False
    st.session_state.username = None
    st.rerun()

# Helper for navigation callback
def navigate_to(page_name):
    st.session_state.page = page_name

# Navigation with session state to allow redirects
if "page" not in st.session_state:
    st.session_state.page = "\ud83d\udcca Dashboard"

page = st.sidebar.radio(
    "Navigation", 
    ["📊 Dashboard", "🧠 Smart Advisor", "🔍 Analysis", "🎯 Budget & Goals", "📋 Transactions", "⚙️ Settings"], 
    label_visibility="collapsed",
    key="page"
)

st.sidebar.markdown("---")
st.sidebar.info(f"✨ **Quote:**\n\n{get_random_quote()}")

# --- DATA PREP ---
df = st.session_state.data
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
    st.title("Dashboard")
    
    if df is None:
        st.info("Please go to 'Settings' to upload your data.")
        st.stop()
    
    # Assert for static analysis
    assert df is not None
        
    # --- SMART ADVISOR INSIGHTS (Top 3) ---
    advisor = FinancialAdvisor(df, st.session_state.salary)
    # Use the new combined insights method
    insights = advisor.get_combined_insights()
    
    if insights:
        with st.container():
            st.markdown("### ⚡ Actionable Insights")
            c1, c2, c3 = st.columns(3)
            cols = [c1, c2, c3]
            for i, insight in enumerate(insights):
                color = "green" if insight['type'] == 'success' else "red" if insight['type'] == 'alert' else "orange"
                with cols[i % 3]:
                    st.markdown(f"""
                    <div style="padding:10px; border-radius:10px 10px 0 0; border:1px solid {color}; border-bottom:0; background-color: rgba(0,0,0,0.2);">
                        <strong style='color:{color}'>{insight['title']}</strong><br>
                        <span style='font-size:0.9em'>{insight['text']}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    target = "📊 Dashboard"
                    if insight['action'] == "Check 'Cutting Expenses' tab": target = "🔍 Analysis"
                    elif insight['action'] == "Cut Dining/Shopping": target = "🎯 Budget & Goals"
                    elif insight['action'] == "Review Rent/Utilities": target = "🔍 Analysis"
                    elif insight['action'] == "Consider Investing": target = "🔍 Analysis"
                    elif insight['action'] == "Check details": target = "🎯 Budget & Goals"
                    elif insight['action'] == "Review Anomalies": target = "🔍 Analysis"
                    elif insight['action'] == "Is this essential?": target = "🎯 Budget & Goals"
                    
                    st.button(insight['action'], key=f"dash_btn_{i}", use_container_width=True, 
                              on_click=navigate_to, args=(target,))

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
            if 'shopping' in cat_lower: icon = "🛍️"
            elif 'food' in cat_lower or 'dining' in cat_lower: icon = "🍔"
            elif 'transport' in cat_lower: icon = "🚗"
            elif 'health' in cat_lower: icon = "💊"
            elif 'utilities' in cat_lower: icon = "💡"
            elif 'entertainment' in cat_lower: icon = "🎬"
            elif 'housing' in cat_lower or 'rent' in cat_lower: icon = "🏠"
            elif 'travel' in cat_lower: icon = "✈️"
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
        st.markdown("### 📥 Export Reports")
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
        st.subheader("🏆 Achievements")
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
                <div style="background-color: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; border-left: 5px solid {color};">
                    <h3 style="margin:0">{title}</h3>
                    <h1 style="margin:0; font-size: 2.5em;">{pct:.1f}%</h1>
                    <p style="opacity:0.7">Target: {target}%</p>
                    <p><strong>{format_currency(convert_amount(data['amount'], curr), curr)}</strong></p>
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
        for insight in insights:
            icon = "✅" if insight['type'] == 'success' else "⚠️" if insight['type'] == 'warning' else "🚨"
            with st.expander(f"{icon} {insight['title']}", expanded=True):
                st.write(insight['text'])
                target = "📊 Dashboard"
                if insight['action'] == "Check 'Cutting Expenses' tab": target = "🔍 Analysis"
                elif insight['action'] == "Cut Dining/Shopping": target = "🎯 Budget & Goals"
                elif insight['action'] == "Review Rent/Utilities": target = "🔍 Analysis"
                elif insight['action'] == "Consider Investing": target = "🔍 Analysis"
                elif insight['action'] == "Check details": target = "🎯 Budget & Goals"
                elif insight['action'] == "Review Anomalies": target = "🔍 Analysis"
                elif insight['action'] == "Is this essential?": target = "🎯 Budget & Goals"
                
                st.button(insight['action'], key=insight['title'], on_click=navigate_to, args=(target,))

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
                st.write(f"🟢 Stocks: **{alloc.get('stocks', 0):.1f}%**")
                st.write(f"🔵 Bonds: **{alloc.get('bonds', 0):.1f}%**")
                st.write(f"🟡 Commodities: **{alloc.get('commodities', 0):.1f}%**")
            with ac2:
                st.markdown("**Ideal Allocation (Target):**")
                st.write(f"🟢 Stocks: **60%**")
                st.write(f"🔵 Bonds: **30%**")
                st.write(f"🟡 Commodities: **10%**")
        else:
            st.info("No investments recorded yet. Add them in Settings to get allocation insights.")
        
        # Investment Suggestions
        st.markdown("---")
        st.subheader("💡 Investment Suggestions")
        
        suggestions = []
        sr = details.get('savings_ratio', 0)
        ir = details.get('investment_ratio', 0)
        
        if sr < 10:
            suggestions.append(("🚨", "Build an Emergency Fund", "Before investing, aim to save at least 3-6 months of expenses. Start by cutting discretionary spending."))
        elif sr < 20:
            suggestions.append(("⚠️", "Increase Savings Rate", f"You're saving {sr:.1f}%. Try to reach 20% by reducing non-essential spending, then invest the surplus."))
        
        if ir < 5:
            suggestions.append(("📌", "Start Investing", "Even small amounts matter. Consider starting with index funds or ETFs for diversification with low fees."))
        elif ir < 15:
            suggestions.append(("📈", "Grow Your Portfolio", f"You're investing {ir:.1f}% of income. Consider increasing to 15-20% through automated monthly investments (SIP/DCA)."))
        
        if total_inv > 0:
            stocks_pct = alloc.get('stocks', 0)
            bonds_pct = alloc.get('bonds', 0)
            if stocks_pct > 80:
                suggestions.append(("⚖️", "Diversify Holdings", "Your portfolio is heavily weighted in stocks. Add bonds/fixed income for stability."))
            elif bonds_pct > 60:
                suggestions.append(("📊", "Consider Growth Assets", "Your portfolio is conservative. If your risk tolerance allows, shift some to equities for long-term growth."))
        
        if score >= 80:
            suggestions.append(("🌟", "Advanced Strategies", "Great financial health! Consider tax-advantaged accounts, real estate, or increasing retirement contributions."))
        
        if not suggestions:
            suggestions.append(("✅", "On Track", "Your finances look healthy. Keep maintaining your savings and investment discipline!"))
        
        for icon, title, desc in suggestions:
            with st.expander(f"{icon} {title}", expanded=True):
                st.write(desc)
        
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
                st.write(f"**{row['name']}**")
                st.progress(min(row['saved_amount']/row['target_amount'], 1.0))
                st.caption(f"{row['saved_amount']} / {row['target_amount']}")
    
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


elif page == "⚙️ Settings":
    st.title("Settings")
    
    st.subheader("Data Upload")
    up_file = st.file_uploader("Upload CSV", type=['csv'])
    if up_file:
        try:
            raw = load_data(up_file)
            pro = preprocess_data(raw)
            cn = st.session_state.categorizer.predict(pro)
            ad = AnomalyDetector()
            fn = ad.detect_anomalies(cn)
            st.session_state.data = fn
            st.success("Loaded!")
        except Exception as e:
            st.error(f"Error: {e}")
            
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
    st.subheader("advanced")
    if st.button("🧠 Retrain Categorization Model"):
        if st.session_state.data is not None:
            with st.spinner("Training model on current data..."):
                st.session_state.categorizer.train(st.session_state.data)
            st.success("Model retrained and saved! Future transactions will be categorized better.")
        else:
            st.warning("No data to train on. Upload a CSV first.")
