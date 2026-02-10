import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime, date

# --- Page Configuration ---
st.set_page_config(page_title="Multi-Loan Debt Strategist", page_icon="🏦", layout="wide")

# --- Session State Initialization ---
if 'theme' not in st.session_state:
    st.session_state.theme = False
if 'loans' not in st.session_state:
    # Example structure: [{'id': 1, 'name': 'Home Loan', 'p': 500000, 'r': 8.5, 'n_years': 20, 'paid_months': 12, 'prepayments': 0}]
    st.session_state.loans = []

# --- Logic: Loan Calculations ---
def calculate_emi(principal, rate_annual, tenure_years):
    if rate_annual <= 0 or tenure_years <= 0: return 0
    r = rate_annual / (12 * 100) # Monthly rate
    n = tenure_years * 12 # Total months
    emi = principal * r * ((1 + r)**n) / (((1 + r)**n) - 1)
    return emi

def get_outstanding_balance(principal, rate_annual, tenure_years, months_paid, total_prepayments=0):
    r = rate_annual / (12 * 100)
    n = tenure_years * 12
    emi = calculate_emi(principal, rate_annual, tenure_years)
    
    # Calculate balance after normal EMI payments
    if months_paid == 0:
        theoretical_bal = principal
    else:
        term1 = principal * ((1 + r)**months_paid)
        term2 = (emi/r) * (((1+r)**months_paid) - 1)
        theoretical_bal = term1 - term2
    
    actual_balance = max(0, theoretical_bal - total_prepayments)
    return actual_balance

def get_amortization_schedule(principal, rate_annual, tenure_years):
    # Simplified schedule generator for charts
    schedule = []
    balance = principal
    r = rate_annual / (12 * 100)
    n = int(tenure_years * 12)
    emi = calculate_emi(principal, rate_annual, tenure_years)
    
    total_interest = 0
    for month in range(1, n + 1):
        interest = balance * r
        principal_paid = emi - interest
        balance -= principal_paid
        total_interest += interest
        
        schedule.append({
            "Month": month,
            "Principal Paid": principal_paid,
            "Interest Paid": interest,
            "Remaining Balance": max(0, balance)
        })
        if balance <= 0: break
    return pd.DataFrame(schedule)

# --- Sidebar ---
with st.sidebar:
    st.title("🏦 Debt Strategist")
    theme = st.toggle("Dark Mode", value=st.session_state.theme)
    st.session_state.theme = theme
    
    st.markdown("---")
    st.header("👤 Your Finances")
    monthly_income = st.number_input("Monthly Income (Net)", min_value=0.0, value=80000.0, step=1000.0)
    
    st.info("💡 **Lump Sum Logic**: Only use cash *excess* of your Emergency Fund (3-6 months expenses).")
    lumpsum_available = st.number_input("One-time Cash Available for Debt", min_value=0.0, value=0.0, step=5000.0, help="Amount you can pay RIGHT NOW to reduce debt.")

    st.markdown("---")
    st.subheader("⚠️ Disclaimer")
    st.caption("Figures are estimates. Pre-payment policies vary by bank.")

# --- Custom CSS ---
if st.session_state.theme:
    st.markdown("""
    <style>
        :root { --primary-color: #F63366; --background-color: #0E1117; --secondary-background-color: #262730; --text-color: #FAFAFA; }
        .stApp { background-color: var(--background-color); color: var(--text-color); }
        .stSidebar { background-color: var(--secondary-background-color); }
        .stMetric { background-color: #1E1E1E !important; padding: 15px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        h1, h2, h3, h4, h5, h6, p, label, li { color: var(--text-color) !important; }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
        .stMetric { 
            background-color: #FFFFFF !important; 
            padding: 15px; 
            border-radius: 8px; 
            border: 1px solid #E0E0E0;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
        [data-testid="stMetricLabel"] {
            color: #666666;
            font-size: 14px;
        }
        [data-testid="stMetricValue"] {
            color: #333333;
            font-size: 24px;
            font-weight: 600;
        }
    </style>
    """, unsafe_allow_html=True)

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
    
    # Estimate remaining months
    # Simple approx: Balance / Principal_portion_of_EMI (varies)
    # Better: use n_years * 12 - paid
    remaining_m = (loan['n'] * 12) - loan['paid']
    if remaining_m > max_tenure_months:
        max_tenure_months = remaining_m

    loans_data.append({
        'name': loan['name'],
        'balance': bal,
        'rate': loan['r'],
        'emi': emi
    })

# Total interest payable (approx for outstanding)
# This is complex for multiple loans with different tenures. 
# We'll sum up the remaining interest of each loan.
total_future_interest = 0
for loan in st.session_state.loans:
    # Schedule for remaining logic is hard without full simulation. 
    # Approx: Total Amount = EMI * Remaining Months
    # Interest = Total Amount - Current Balance
    rem_months = max(0, (loan['n'] * 12) - loan['paid'])
    # If using balance, we assume standard schedule from here? 
    # Actually, if prepayments happened, EMI stays same (usually) but tenure reduces.
    # We need to solve for new n given current Balance and EMI.
    if loan['p'] > 0 and loan['r'] > 0:
         r_mo = loan['r'] / 1200
         current_emi = calculate_emi(loan['p'], loan['r'], loan['n'])
         current_bal = get_outstanding_balance(loan['p'], loan['r'], loan['n'], loan['paid'], loan['extra_paid'])
         
         if current_bal > 0:
             # n = -log(1 - r*P/E) / log(1+r)
             try:
                 val = 1 - (r_mo * current_bal / current_emi)
                 if val > 0:
                     real_rem_months = -np.log(val) / np.log(1 + r_mo)
                     total_pay_future = real_rem_months * current_emi
                     future_int = total_pay_future - current_bal
                     total_future_interest += future_int
             except:
                 pass

total_amount_payable = total_outstanding + total_future_interest
payoff_year = date.today().year + int(max_tenure_months/12)

# --- Tabs ---
# Renamed to match screenshot
tab1, tab2, tab3 = st.tabs(["📊 Dashboard & Schedule", "🧠 Smart Application", "🔄 Balance Transfer"])

# --- TAB 1: Dashboard & Schedule ---
with tab1:
    st.header("Loan Overview")
    
    # 1. Metrics Row
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Monthly EMI", f"₹{total_emi:,.2f}")
    m2.metric("Total Interest (Future)", f"₹{total_future_interest:,.2f}", help="Estimated remaining interest to be paid")
    m3.metric("Total Amount (Outstanding)", f"₹{total_amount_payable:,.2f}", help="Principal + Interest Remaining")
    m4.metric("Payoff Date", f"{payoff_year} (Approx)")
    
    st.markdown("---")

    # 2. Charts Row
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.subheader("Amortization Curve (Aggregate)")
        if not st.session_state.loans:
            st.info("Add a loan to see the curve.")
            chart_data = pd.DataFrame({'Month': [], 'Amount': [], 'Type': []})
        else:
            # Generate aggregate schedule
            # This is tricky fast. We'll simplify: 
            # Show the largest loan's curve or stack them?
            # Let's stack the balances of all loans over time (up to max tenure).
            
            # Simulation
            months = range(1, int(max_tenure_months) + 1)
            agg_schedule = []
            
            # Make a copy of balances
            current_balances = [l['balance'] for l in loans_data]
            current_emis = [l['emi'] for l in loans_data]
            current_rates = [l['rate']/1200 for l in loans_data]
            
            for m in months:
                p_paid_month = 0
                i_paid_month = 0
                
                for i in range(len(current_balances)):
                    if current_balances[i] > 0:
                        interest = current_balances[i] * current_rates[i]
                        principal = current_emis[i] - interest
                        
                        # Check if last payment
                        if principal > current_balances[i]:
                            principal = current_balances[i]
                            interest = 0 # simplified last bit
                        
                        current_balances[i] -= principal
                        p_paid_month += principal
                        i_paid_month += interest
                
                agg_schedule.append({
                    "Month": m,
                    "Principal Paid": p_paid_month,
                    "Interest Paid": i_paid_month
                })
                if sum(current_balances) <= 1: break
            
            chart_df = pd.DataFrame(agg_schedule)
            chart_melt = chart_df.melt('Month', var_name='Type', value_name='Amount')
            
            chart = alt.Chart(chart_melt).mark_area().encode(
                x='Month',
                y='Amount',
                color=alt.Color('Type', scale=alt.Scale(domain=['Interest Paid', 'Principal Paid'], range=['#1f77b4', '#aec7e8'])),
                tooltip=['Month', 'Type', 'Amount']
            ).interactive()
            st.altair_chart(chart, use_container_width=True)

    with c2:
        st.subheader("Principal vs Interest")
        if total_outstanding > 0:
            pie_data = pd.DataFrame({
                'Category': ['Principal', 'Total Interest'],
                'Amount': [total_outstanding, total_future_interest]
            })
            pie = alt.Chart(pie_data).mark_arc(innerRadius=60).encode(
                theta='Amount',
                color=alt.Color('Category', scale=alt.Scale(domain=['Principal', 'Total Interest'], range=['#1f77b4', '#aec7e8'])),
                tooltip=['Category', 'Amount']
            )
            st.altair_chart(pie, use_container_width=True)
        else:
            st.caption("No outstanding debt.")

    # 3. Loan Management Section (Moved to bottom of dashboard)
    with st.expander("📝 Manage Your Loans (Add / Remove)", expanded=False):
        col_add, col_list = st.columns([1, 2])
        with col_add:
            with st.form("add_loan_dash"):
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
                    if cols[3].button("🗑", key=f"d{i}"):
                        st.session_state.loans.pop(i)
                        st.rerun()

# --- TAB 2: Smart Application (Analysis & Strategy) ---
with tab2:
    st.header("🧠 Smart Application")
    
    # 1. Health Alert (Moved from old tab)
    if monthly_income > 0:
        dti = (total_emi / monthly_income) * 100
        if dti > 20:
             st.error(f"🚨 **High Debt Burden**: EMI is {dti:.1f}% of Income (>20%). Suggest Aggressive Repayment.")
        else:
            st.success(f"✅ **Healthy Status**: EMI is {dti:.1f}% of Income.")
    
    st.divider()
    
    # 2. Strategy Engine
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
with tab3:
    st.header("🔄 Balance Transfer Analysis")
    st.write("Compare your loans with a new offer.")
    
    if not st.session_state.loans:
        st.info("Add loans first.")
    else:
        loan_names = [l['name'] for l in st.session_state.loans]
        selected_loan_name = st.selectbox("Select Loan to Transfer", loan_names)
        
        # Find loan data
        selected_loan = next((l for l in st.session_state.loans if l['name'] == selected_loan_name), None)
        
        if selected_loan:
             # Balance Calc
             cur_bal = get_outstanding_balance(selected_loan['p'], selected_loan['r'], selected_loan['n'], selected_loan['paid'], selected_loan['extra_paid'])
             
             c1, c2 = st.columns(2)
             with c1:
                 st.markdown("#### New Offer Details")
                 new_r = st.number_input("New Interest Rate (%)", 0.1, 20.0, 8.5)
                 proc_fee = st.number_input("Processing Fee (%)", 0.0, 5.0, 0.5)
                 other_cost = st.number_input("Fixed Costs", 0.0, 10000.0, 2000.0)
                 
             with c2:
                 st.markdown("#### Comparison")
                 
                 # Current Future Interest (Approx)
                 rem_months = max(0, (selected_loan['n'] * 12) - selected_loan['paid'])
                 current_future_int = 0
                 
                 if cur_bal > 0 and selected_loan['r'] > 0:
                     # Calculate total payable if we continue same schedule
                     emi = calculate_emi(selected_loan['p'], selected_loan['r'], selected_loan['n'])
                     # Strictly speaking this EMI continues for remaining tenure
                     # But current balance might be lower due to prepayments
                     # Let's simplify: New Loan Amount = Cur Bal + Fees
                     # Compare (Old Inteest Remaining) vs (New Interest + Fees)
                     
                     # 1. Old Interest Remaining
                     # Re-amortize current balance over remaining months at old rate? 
                     # Or just (EMI * Rem_Months) - Cur_bal?
                     # Let's use (EMI * Rem_Months) - Cur_bal as robust approx
                     old_total_pay = emi * rem_months
                     old_int_rem = max(0, old_total_pay - cur_bal)
                     
                     st.metric("Current Future Interest", f"₹{old_int_rem:,.0f}")
                     
                     # 2. New Loan
                     # New Loan Amount = Cur_Bal + Processing Fees + Fixed Costs
                     transfer_cost = (cur_bal * proc_fee / 100) + other_cost
                     new_principal = cur_bal + transfer_cost
                     
                     # New EMI (Assume same remaining tenure for comparison)
                     new_n_years = rem_months / 12
                     if new_n_years < 0.1: new_n_years = 1.0 # Edge case
                     
                     new_emi = calculate_emi(new_principal, new_r, new_n_years)
                     new_total_pay = new_emi * rem_months
                     new_int = new_total_pay - new_principal
                     
                     st.metric("New Future Interest", f"₹{new_int:,.0f}")
                     st.caption(f"Includes Transfer Costs: ₹{transfer_cost:,.0f}")
                     
                     # Result
                     savings = old_int_rem - (new_int + transfer_cost)
                     # Wait, transfer cost is already inside new_principal -> new_int calculation involved it?
                     # Total Cost Old = Cur_Bal + Old_Int
                     # Total Cost New = (Cur_Bal + Transfer_Cost) + New_Int
                     # Difference = (Old_Int) - (Transfer_Cost + New_Int)
                     
                     diff = old_int_rem - (new_int + transfer_cost) 
                     # Actually transfer cost is paid upfront or capitalized? 
                     # If capitalized (added to loan), then we pay interest on it. 
                     # My calc above `new_principal = cur_bal + transfer_cost` assumes capitalization.
                     # So `new_total_pay` is what we pay. 
                     # Old pay = `old_total_pay`
                     # Savings = old_total_pay - new_total_pay
                     
                     final_savings = old_total_pay - new_total_pay
                     
                     st.divider()
                     if final_savings > 0:
                         st.success(f"✅ **Switch & Save**: You will save **₹{final_savings:,.0f}** over the remaining tenure!")
                     else:
                         st.error(f"❌ **Don't Switch**: You will lose **₹{abs(final_savings):,.0f}**.")
