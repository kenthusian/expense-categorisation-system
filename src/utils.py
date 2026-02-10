import altair as alt  # type: ignore
import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
import json
import random
import os

def get_random_quote():
    """
    Returns a random financial quote from the JSON file.
    """
    try:
        # Construct absolute path to ensure it works
        base_path = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_path, 'quotes.json')
        
        with open(file_path, 'r', encoding='utf-8') as f:
            quotes = json.load(f)
        return random.choice(quotes)
    except Exception as e:
        return "Save money and money will save you."


def render_charts(df):
    """
    Renders interactive charts using Altair.
    """
    if 'category' not in df.columns:
        st.warning("No category column found for visualization.")
        return

    # Filter out Income for the pie chart
    expenses_df = df[df['category'] != 'Income'].copy()
    if expenses_df.empty:
        st.info("No expense data to visualize.")
        return

    # Aggregate proper formatting
    # ensure amount is positive
    expenses_df['amount'] = expenses_df['amount'].abs()
    
    category_totals = expenses_df.groupby('category')['amount'].sum().reset_index()

    # Interactive Pie Chart (Donut)
    base = alt.Chart(category_totals).encode(
        theta=alt.Theta("amount", stack=True)
    )

    pie = base.mark_arc(outerRadius=120, innerRadius=80).encode(
        color=alt.Color("category"),
        order=alt.Order("amount", sort="descending"),
        tooltip=["category", "amount"]
    )
    
    text = base.mark_text(radius=140).encode(
        text=alt.Text("amount", format=",.1f"),
        order=alt.Order("amount", sort="descending"),
        color=alt.value("black")  
    )

    st.altair_chart(pie + text, use_container_width=True)

def convert_amount(amount, currency):
    """
    Simulated currency conversion.
    Base currency is INR (since dummy data seems to be INR based given the amounts).
    """
    # Exchange rates relative to INR (Approximate)
    rates = {
        "INR": 1.0,
        "USD": 0.012,
        "EUR": 0.011,
        "GBP": 0.0095,
        "JPY": 1.77
    }
    
    rate = rates.get(currency, 1.0)
    return amount * rate

def format_currency(amount, currency):
    """
    Formats amount with currency symbol.
    """
    symbols = {
        "INR": "₹",
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "JPY": "¥"
    }
    symbol = symbols.get(currency, "")
    return f"{symbol}{amount:,.2f}"

# --- EXPORT HELPERS ---

from io import BytesIO
from fpdf import FPDF  # type: ignore
import matplotlib.pyplot as plt  # type: ignore

def generate_excel(df):
    """
    Generates an Excel file from the dataframe.
    """
    output = BytesIO()
    # ExcelWriter requires openpyxl installed
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Transactions')
    return output.getvalue()

def generate_pdf(df, currency_name, health_details=None):
    """
    Generates a PDF report from the dataframe with charts, top transactions, and advice.
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Calculate usable width
    effective_width = pdf.w - 2 * pdf.l_margin
    
    pdf.set_font("helvetica", "B", 18)
    
    # 1. Header
    pdf.cell(0, 15, "Personal Finance Report", ln=True, align='C')
    pdf.set_font("helvetica", "", 12)
    pdf.cell(0, 10, f"Currency: {currency_name}", ln=True, align='C')
    pdf.ln(5)

    def pdf_fmt(amt):
        return f"{currency_name} {amt:,.2f}"

    # Logic Separation
    # We assume 'Income' is the specific category name for income
    # Use keywords to identify income if category isn't explicit
    income_cats = ['Income', 'Salary', 'Deposit', 'Bonus']
    # Better mask: check if category is in list OR amount is positive (if we trust data)
    # But usually expenses are negative in some exports, positive in others. 
    # App logic: Income categories are defined.
    
    mask_income = df['category'].isin(income_cats)
    income_df = df[mask_income]
    
    # Create working copies
    inc_copy = income_df.copy()
    exp_copy = df[~mask_income].copy()
    
    total_income = inc_copy['amount'].sum()
    total_expense = exp_copy['amount'].sum() 
    
    total_expense_abs = abs(total_expense)
    balance = total_income - total_expense_abs # Simplified Net Math
    
    # 2. Summary Section
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, "1. Executive Summary", ln=True)
    pdf.set_font("helvetica", "", 11)
    
    pdf.cell(40, 8, "Total Income:", 0)
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(0, 8, pdf_fmt(total_income), ln=True)
    
    pdf.set_font("helvetica", "", 11)
    pdf.cell(40, 8, "Total Expenses:", 0)
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(0, 8, pdf_fmt(total_expense_abs), ln=True)
    
    pdf.set_font("helvetica", "", 11)
    pdf.cell(40, 8, "Net Balance:", 0)
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(0, 8, pdf_fmt(balance), ln=True)
    pdf.ln(10)

    # 3. CHART SECTION (Category Breakdown)
    if not exp_copy.empty:
        pdf.set_font("helvetica", "B", 14)
        pdf.cell(0, 10, "2. Expense Category Breakdown", ln=True)
        
        # Aggregate
        # Ensure positive amounts for pie chart
        exp_copy['abs_amount'] = exp_copy['amount'].abs()
        cat_exp = exp_copy.groupby('category')['abs_amount'].sum()
        
        plt.figure(figsize=(6, 4))
        plt.pie(cat_exp, labels=cat_exp.index, autopct='%1.1f%%', colors=plt.cm.Paired.colors)
        plt.title('Expenses by Category')
        
        img_buf = BytesIO()
        plt.savefig(img_buf, format='png', bbox_inches='tight')
        plt.close()
        
        temp_img_path = "temp_cat_chart.png"
        with open(temp_img_path, "wb") as f:
            f.write(img_buf.getvalue())
            
        pdf.image(temp_img_path, x=40, w=130)
        pdf.ln(5)
        if os.path.exists(temp_img_path): os.remove(temp_img_path)

    # 4. TRENDS SECTION
    if 'date' in df.columns:
        pdf.add_page()
        pdf.set_font("helvetica", "B", 14)
        pdf.cell(0, 10, "3. Financial Trends", ln=True)
        
        try:
            df['date'] = pd.to_datetime(df['date'])
            daily_spend = df[~mask_income].groupby('date')['amount'].sum().abs()
            
            plt.figure(figsize=(10, 4))
            plt.plot(daily_spend.index, daily_spend.values, marker='o', linestyle='-', color='r')
            plt.title('Daily Spending Trend')
            plt.xlabel('Date')
            plt.ylabel(f'Amount ({currency_name})')
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.tight_layout()
            
            img_buf = BytesIO()
            plt.savefig(img_buf, format='png', bbox_inches='tight')
            plt.close()
            
            temp_trend_path = "temp_trend_chart.png"
            with open(temp_trend_path, "wb") as f:
                f.write(img_buf.getvalue())
            
            pdf.image(temp_trend_path, x=10, w=190)
            pdf.ln(5)
            if os.path.exists(temp_trend_path): os.remove(temp_trend_path)
        except Exception as e:
            pdf.set_font("helvetica", "I", 10)
            pdf.cell(0, 10, f"Could not generate trend chart: {e}", ln=True)

    # 5. HEALTH AND INSIGHTS SECTION
    if health_details:
        pdf.add_page()
        pdf.set_font("helvetica", "B", 14)
        pdf.cell(0, 10, "4. Financial Health Analysis", ln=True)
        pdf.ln(5)
        
        # Metrics Table
        pdf.set_font("helvetica", "B", 11)
        pdf.set_fill_color(240, 240, 240)
        
        pdf.cell(90, 10, "Metric", border=1, fill=True)
        pdf.cell(90, 10, "Value", border=1, fill=True, ln=True)
        
        pdf.set_font("helvetica", "", 10)
        
        metrics = [
            ("Savings Ratio", f"{health_details.get('savings_ratio', 0):.1f}%"),
            ("Investment Ratio", f"{health_details.get('investment_ratio', 0):.1f}%"),
            ("Net Savings", pdf_fmt(health_details.get('net_savings', 0))),
            ("Total Invested", pdf_fmt(health_details.get('total_invested', 0)))
        ]
        
        for m, v in metrics:
            pdf.cell(90, 8, m, border=1)
            pdf.cell(90, 8, v, border=1, ln=True)
            
        pdf.ln(5)
        
        # Allocation
        alloc = health_details.get('allocation', {})
        if alloc:
            pdf.set_font("helvetica", "B", 12)
            pdf.cell(0, 10, "Investment Allocation", ln=True)
            pdf.set_font("helvetica", "", 10)
            pdf.cell(0, 6, f"Stocks: {alloc.get('stocks', 0):.1f}% | Bonds: {alloc.get('bonds', 0):.1f}% | Commodities: {alloc.get('commodities', 0):.1f}%", ln=True)
            pdf.ln(5)

        # Suggestions
        # Re-derive suggestions based on score logic locally since we passed just details
        # Or if details included suggestions list. 
        # App logic return: total_score, details. details has: savings_score, etc.
        # Let's add generic advice based on savings ratio
        pdf.set_font("helvetica", "B", 12)
        pdf.cell(0, 10, "AI Recommendations", ln=True)
        pdf.set_font("helvetica", "", 10)
        
        sr = health_details.get('savings_ratio', 0)
        ir = health_details.get('investment_ratio', 0)
        
        advice = []
        if sr < 20:
            advice.append("- Your savings ratio is below 20%. Try to cut discretionary spending (Dining, Entertainment).")
        else:
            advice.append("- Good savings habit! Keep maintaining at least 20%.")
            
        if ir < 10:
            advice.append("- Investment ratio is low (<10%). Consider starting an SIP or index fund investment.")
        elif alloc.get('stocks', 0) < 50 and sr > 30:
             advice.append("- You have high savings but low stock exposure. Consider diversifying into equities for long term growth.")
             
        for adv in advice:
            pdf.multi_cell(0, 6, adv)
            pdf.ln(2)

    # 6. FULL TRANSACTION LOG
    pdf.add_page()
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, "5. Detailed Transaction Log", ln=True)
    pdf.ln(5)
    
    pdf.set_font("helvetica", "B", 10)
    pdf.set_fill_color(200, 220, 255)
    cols = ["Description", "Category", "Amount"]
    col_widths = [90, 50, 50]
    
    for i in range(len(cols)):
        pdf.cell(col_widths[i], 10, cols[i], border=1, fill=True, align='C')
    pdf.ln()
    
    pdf.set_font("helvetica", "", 9)
    for _, row in df.iterrows():
        # Truncate description
        desc = str(row.get('description', ''))[:50]  # type: ignore
        cat = str(row.get('category', ''))[:25]  # type: ignore
        amt = row.get('amount', 0)
        
        pdf.cell(col_widths[0], 8, desc, border=1)
        pdf.cell(col_widths[1], 8, cat, border=1)
        pdf.cell(col_widths[2], 8, pdf_fmt(amt), border=1, align='R')
        pdf.ln()

    pdf_output = pdf.output(dest='S')
    if isinstance(pdf_output, str):
        return pdf_output.encode('latin-1')
    return bytes(pdf_output)  # type: ignore
