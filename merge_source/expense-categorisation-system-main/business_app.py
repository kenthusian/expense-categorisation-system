import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
from src.data_processor import load_data, preprocess_data
from src.business_model import BusinessExpenseCategorizer

st.set_page_config(page_title="Business Finance & GST Manager", layout="wide", page_icon="🏢")

# --- CSS & Theme ---
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
    }
    .stMetric {
        background-color: transparent !important;
    }
    /* Dark mode adjustments would go here if needed */
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---
st.sidebar.title("🏢 Business Finance")
st.sidebar.markdown("---")

# File Upload
uploaded_file = st.sidebar.file_uploader("Upload Business Statement (CSV)", type=['csv'])

# Default to dummy data if nothing uploaded
if uploaded_file is None:
    USE_DUMMY = True
    st.sidebar.info("Using demo data. Upload a CSV to customize.")
else:
    USE_DUMMY = False

    USE_DUMMY = False

# Sidebar Filters
st.sidebar.markdown("### 🗓️ Period Filter")


st.sidebar.markdown("### 🏛️ Tax Settings")
tax_bracket = st.sidebar.selectbox("Corporate Tax Bracket", options=[15, 22, 25, 30, 0], format_func=lambda x: f"{x}%", help="Select applicable income tax rate")
tax_rate = tax_bracket / 100.0

# --- Theme Toggle ---
st.sidebar.markdown("### 🎨 Theme Settings")
theme = st.sidebar.toggle("Dark Mode", value=False)

if theme:
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
        .stSidebar, .stSidebar > div {
            background-color: var(--secondary-background-color);
        }
        h1, h2, h3, h4, h5, h6, p, div, span, label, li {
            color: var(--text-color) !important;
        }
        .stMetric {
            background-color: #1E1E1E !important;
            padding: 10px;
            border-radius: 5px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        .stDataFrame {
            color: var(--text-color);
        }
    </style>
    """, unsafe_allow_html=True)
else:
    # Light Mode Styling for Cards
    st.markdown("""
    <style>
        .stMetric {
            background-color: #F8F9FB !important;
            padding: 10px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            border: 1px solid #E0E0E0;
        }
    </style>
    """, unsafe_allow_html=True)

# --- Initialize Model ---
if 'business_categorizer' not in st.session_state:
    st.session_state.business_categorizer = BusinessExpenseCategorizer()

categorizer = st.session_state.business_categorizer

# --- Load Data ---
@st.cache_data
def load_and_prep(file_path_or_buffer):
    if isinstance(file_path_or_buffer, str):
        df = pd.read_csv(file_path_or_buffer)
    else:
        df = pd.read_csv(file_path_or_buffer)
    
    # Normalize
    df.columns = [c.lower().strip() for c in df.columns]
    
    # Ensure Date
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
    
    return df

try:
    if USE_DUMMY:
        df = load_and_prep("dummy_business_data.csv")
    else:
        df = load_and_prep(uploaded_file)
        
    # Preprocess (clean description)
    df = preprocess_data(df)
    
    # Run Categorization (if not already present or if we want to override)
    # For business app, let's assume we want to predict 'category' if it's missing or if we just want to run the model
    # Use the model logic
    df = categorizer.predict(df)
    
    # Ensure GST columns exist, else calc default
    if 'gst_rate' not in df.columns:
        df['gst_rate'] = 0.0 # Default to 0 if unknown
    if 'gst_amount' not in df.columns:
        # Rough calc: amount is inclusive or exclusive? 
        # Let's assume amount in CSV is Transaction Amount. 
        # If we don't have GST info, we can't guess easily. 
        # For this prototype, set to 0.
        df['gst_amount'] = 0.0

except FileNotFoundError:
    st.error("Dummy data not found. Please generate it first.")
    st.stop()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# --- Date Filtering ---
min_date = df['date'].min().date()
max_date = df['date'].max().date()

start_date = st.sidebar.date_input("Start Date", min_date)
end_date = st.sidebar.date_input("End Date", max_date)

if start_date > end_date:
    st.sidebar.error("Start date must be before end date.")

# Filter Data
mask = (df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)
df_filtered = df.loc[mask]

# --- PDF Report Sidebar (After Data Load) ---
st.sidebar.markdown("### 📄 Reports")
if not df.empty:
    df['fiscal_year'] = df['date'].apply(lambda x: x.year + 1 if x.month >= 4 else x.year)
    available_years = sorted(df['fiscal_year'].unique(), reverse=True)
    selected_years_report = st.sidebar.multiselect("Select Years for Report", available_years, default=available_years[:1])
    
    if st.sidebar.button("Generate PDF Report"):
        from src.pdf_generator import generate_pdf_report
        with st.spinner("Generating PDF..."):
            pdf = generate_pdf_report(df, selected_years_report, tax_rate)
            # Output to string/bytes
            pdf_output = pdf.output(dest='S').encode('latin-1') # 'S' returns document as string. encode to bytes.
            
            st.sidebar.download_button(
                label="⬇️ Download PDF",
                data=pdf_output,
                file_name=f"Financial_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf"
            )

# --- Main Tabs ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "📝 GST Analysis", "❤️ Financial Health", "📂 Data"])

# --- TAB 1: DASHBOARD ---
# Helper for Indian Currency Formatting
def format_indian_currency(value):
    try:
        val = float(value)
    except:
        return value
    if abs(val) >= 10000000: # 1 Crore
        return f"₹{val/10000000:.2f} Cr"
    elif abs(val) >= 100000: # 1 Lakh
        return f"₹{val/100000:.2f} L"
    else:
        return f"₹{val:,.2f}"

# --- TAB 1: DASHBOARD ---
with tab1:
    st.header("Business Overview")
    
    # --- Current Year Snapshot ---
    # Determine latest Fiscal Year
    max_date = df['date'].max()
    current_fy_year = max_date.year + 1 if max_date.month >= 4 else max_date.year
    fy_start = pd.Timestamp(f"{current_fy_year-1}-04-01")
    fy_end = pd.Timestamp(f"{current_fy_year}-03-31")
    
    current_fy_df = df[(df['date'] >= fy_start) & (df['date'] <= fy_end)]

    if not current_fy_df.empty:
        st.subheader(f"📌 Current Financial Year (FY{current_fy_year}) Snapshot")
        
        # FY Metrics
        cy_rev = current_fy_df[current_fy_df['amount'] > 0]['amount'].sum()
        cy_exp = current_fy_df[current_fy_df['amount'] < 0]['amount'].sum()
        cy_profit = cy_rev + cy_exp
        
        # Tax
        cy_tax = max(0, cy_profit * tax_rate)
        cy_pat = cy_profit - cy_tax
        
        # GST
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
    
    # KPI Logic for Filtered Data
    # ... (existing logic follows)
    
    total_revenue = df_filtered[df_filtered['amount'] > 0]['amount'].sum()
    total_expenses = df_filtered[df_filtered['amount'] < 0]['amount'].sum() # This is negative
    net_profit = total_revenue + total_expenses
    
    # GST Logic
    # GST Output (Collected on Revenue)
    gst_collected = df_filtered[df_filtered['amount'] > 0]['gst_amount'].sum()
    
    # GST Input (Paid on Expenses)
    # In generated data, gst_amount is positive absolute value usually? 
    # Let's check generation: gst_amount = base * rate. It is absolute.
    gst_paid = df_filtered[df_filtered['amount'] < 0]['gst_amount'].sum()
    
    net_gst_payable = gst_collected - gst_paid
    
    # User Rule: If Net Profit is negative, GST Payable is 0
    if net_profit < 0:
        net_gst_payable = 0
    
    # Income Tax Calculation
    income_tax = max(0, net_profit * tax_rate)
    net_profit_post_tax = net_profit - income_tax

    # KPIs
    st.markdown("### Key Metrics")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Revenue", format_indian_currency(total_revenue))
    c2.metric("Total Expenses", format_indian_currency(abs(total_expenses)))
    c3.metric("Net Profit (Pre-Tax)", format_indian_currency(net_profit), delta_color="normal")
    c4.metric("Net GST Payable", format_indian_currency(net_gst_payable), help="Output GST - Input GST (Adjusted to 0 if Loss)")
    
    c5, c6 = st.columns(2)
    c5.metric("Income Tax Payable", format_indian_currency(income_tax), help=f"Calculated at {tax_bracket}% on Net Profit")
    c6.metric("Net Profit (Post-Tax)", format_indian_currency(net_profit_post_tax))

    # Charts
    c_chart1, c_chart2 = st.columns(2)
    
    with c_chart1:
        st.subheader("Income vs Expenses")
        # Group by Month
        df_chart = df_filtered.copy()
        df_chart['month'] = df_chart['date'].dt.strftime('%Y-%m')
        df_chart['type'] = df_chart['amount'].apply(lambda x: 'Income' if x > 0 else 'Expense')
        df_chart['abs_amount'] = df_chart['amount'].abs()
        
        chart = alt.Chart(df_chart).mark_bar().encode(
            x='month',
            y='sum(abs_amount)',
            color='type',
            tooltip=['month', 'type', 'sum(abs_amount)']
        ).properties(title="Monthly Trends")
        st.altair_chart(chart, use_container_width=True)
        
    with c_chart2:
        st.subheader("Expenses by Category")
        expense_df = df_filtered[df_filtered['amount'] < 0].copy()
        expense_df['abs_amount'] = expense_df['amount'].abs()
        
        pie = alt.Chart(expense_df).mark_arc().encode(
            theta=alt.Theta("sum(abs_amount)", stack=True),
            color=alt.Color("category"),
            tooltip=["category", alt.Tooltip("sum(abs_amount)", format=",")]
        ).properties(title="Expense Breakdown")
        st.altair_chart(pie, use_container_width=True)

# --- TAB 2: GST ANALYSIS ---
with tab2:
    st.header("GST Analysis & Filing Helper")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📥 Input Tax Credit (ITC)")
        st.metric("Total GST Paid on Expenses", f"₹{gst_paid:,.2f}")
        st.caption("This is the tax you paid on purchases/expenses. You can claim this back.")
        
    with col2:
        st.markdown("### 📤 Output GST Liability")
        st.metric("Total GST Collected on Sales", f"₹{gst_collected:,.2f}")
        st.caption("This is the tax you collected from clients. You owe this to the govt.")
        
    st.divider()
    
    st.subheader("Net Position")
    if net_gst_payable > 0:
        st.error(f"You need to pay ₹{net_gst_payable:,.2f} to the Government.")
    else:
        st.success(f"You have a GST Credit of ₹{abs(net_gst_payable):,.2f} to carry forward.")
        
    st.subheader("Transaction-wise GST Details")
    gst_table = df_filtered[['date', 'description', 'category', 'amount', 'gst_rate', 'gst_amount']].copy()
    gst_table['type'] = gst_table['amount'].apply(lambda x: 'Sale' if x > 0 else 'Purchase')
    st.dataframe(gst_table, use_container_width=True)

# --- TAB 3: FINANCIAL HEALTH ---
with tab3:
    st.header("Business Health Score")
    
    # Simple Health Logic
    # 1. Profit Margin
    if total_revenue > 0:
        margin = (net_profit / total_revenue) * 100
    else:
        margin = 0
        
    # 2. Expense Ratio
    # 3. Burn Rate (Avg Monthly Expense)
    num_months = (df_filtered['date'].max() - df_filtered['date'].min()).days / 30
    if num_months < 1: num_months = 1
    burn_rate = abs(total_expenses) / num_months
    
    # 4. Runway (Assume we have cash balance? We don't know cash balance. Skip.)
    
    st.metric("Net Profit Margin", f"{margin:.1f}%")
    
    # Score Calculation (0-100)
    # Healthy margin > 20%
    score = 0
    if margin > 30: score += 40
    elif margin > 15: score += 25
    elif margin > 0: score += 10
    
    # Revenue Growth (Compare last month vs avg)
    # ... Simplified for MVP
    
    # Stability
    if net_profit > 0: score += 30
    
    # GST Compliance (just mock check)
    score += 30 # Assume compliance
    
    st.progress(score/100)
    st.write(f"**Business Health Score: {score}/100**")
    
    if score < 50:
        st.warning("Profit margins are low. Review overhead costs (Rent, Software, Travel).")
    else:
        st.success("Business is healthy! Maintain sales velocity.")
        
    st.markdown("---")
    st.header("📈 5-Year Financial Trend (2021-2026)")
    
    # Process full 5-year data (df) regardless of date filter
    df_annual = df.copy()
    df_annual['year'] = df_annual['date'].dt.year
    # Group by financial year (Apr to Mar). 
    # Simply using calendar year for MVP visualization or Fiscal? 
    # User asked for "Last 5 Years". Let's stick to Calendar Year logic for simplicity in grouping, 
    # or better, Fiscal Year if data starts April.
    # Let's use 'Year' column which we just created (Calendar Year). 
    # Data is 2021-04 to 2026-03. So 2021 is partial?
    # Actually, 2021-04 to 2022-03 is FY22.
    # Let's do Fiscal Year grouping.
    df_annual['fiscal_year'] = df_annual['date'].apply(lambda x: x.year + 1 if x.month >= 4 else x.year)
    
    # Aggregations
    annual_stats = []
    
    # Mock starting values for Assets/Liabilities (Start of period)
    current_assets = 5000000.0 
    current_liabilities = 2000000.0
    
    years = sorted(df_annual['fiscal_year'].unique())
    # Exclude partial current year if needed? 2026 is partial (ends Mar 31). Actually generated to Mar 31, so complete.
    
    for year in years:
        # Filter for FY
        fy_start = pd.Timestamp(f"{year-1}-04-01")
        fy_end = pd.Timestamp(f"{year}-03-31")
        
        year_data = df_annual[(df_annual['date'] >= fy_start) & (df_annual['date'] <= fy_end)]
        
        if year_data.empty: continue
        
        revenue = year_data[year_data['amount'] > 0]['amount'].sum()
        expenses = year_data[year_data['amount'] < 0]['amount'].sum()
        net_profit = revenue + expenses
        
        # Calculate Tax for History
        hist_tax = max(0, net_profit * tax_rate)
        pat = net_profit - hist_tax

        # EBITDA Components
        interest = year_data[year_data['category'] == 'Interest']['amount'].abs().sum()
        depreciation = year_data[year_data['category'] == 'Depreciation']['amount'].abs().sum()
        
        ebitda = net_profit + interest + depreciation
        
        # Assets Update (Retained Earnings uses Post-Tax Profit now)
        current_assets += pat
        
        # Liabilities Update (Mock: Repay some, borrow some)
        # E.g. Liability decreases by interest payment principal proxy? 
        # Let's say we pay off 10% of liability each year but take new loans if Net Profit is low?
        # Simple simulation:
        current_liabilities = current_liabilities * 0.9 # Pay down 10%
        if pat < 0: 
            current_liabilities += abs(pat) # Borrow to cover loss
            
        annual_stats.append({
            'Fiscal Year': f"FY{year}",
            'Revenue': revenue,
            'Net Profit (Pre-Tax)': net_profit,
            'Income Tax': hist_tax,
            'Net Profit (Post-Tax)': pat,
            'EBITDA': ebitda,
            'Assets': current_assets,
            'Liabilities': current_liabilities
        })
        
    stats_df = pd.DataFrame(annual_stats)
    
    if not stats_df.empty:
        # Calculate % Growth
        cols_to_calc = ['Revenue', 'Net Profit (Pre-Tax)', 'Net Profit (Post-Tax)', 'EBITDA', 'Assets', 'Liabilities']
        for col in cols_to_calc:
            stats_df[f'{col} Growth %'] = stats_df[col].pct_change() * 100
        
        # Display Table
        st.subheader("Annual Financial Metrics")
        
        # Formatting for display
        display_df = stats_df.copy()
        for col in cols_to_calc:
            display_df[col] = display_df[col].apply(lambda x: f"₹{x:,.2f}")
            display_df[f'{col} Growth %'] = display_df[f'{col} Growth %'].apply(lambda x: f"{x:+.2f}%" if pd.notnull(x) else "-")
            
        st.dataframe(display_df, use_container_width=True)
        
        # Charts
        st.subheader("Trend Visualization")
        metric_to_plot = st.selectbox("Select Metric to Visualize", cols_to_calc)
        
        chart = alt.Chart(stats_df).mark_line(point=True).encode(
            x='Fiscal Year',
            y=metric_to_plot,
            tooltip=['Fiscal Year', metric_to_plot, f'{metric_to_plot} Growth %']
        ).properties(title=f"{metric_to_plot} over 5 Years")
        
        st.altair_chart(chart, use_container_width=True)

# --- TAB 4: DATA ---
with tab4:
    st.header("Data Management")
    
    # Editable Data
    edited_df = st.data_editor(df_filtered, num_rows="dynamic")
    
    # Retrain Button
    if st.button("Training Model on Current Data"):
        with st.spinner("Training..."):
            try:
                categorizer.train(edited_df)
                st.success("Model retrained successfully!")
            except Exception as e:
                st.error(f"Training failed: {e}")
                
    # Download
    st.download_button(
        label="Download Processed Data",
        data=edited_df.to_csv(index=False).encode('utf-8'),
        file_name='business_financial_data.csv',
        mime='text/csv',
    )
