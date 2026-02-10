from fpdf import FPDF
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import tempfile
import os

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Business Financial Report', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 6, title, 0, 1, 'L', 1)
        self.ln(4)

    def chapter_body(self, body):
        self.set_font('Arial', '', 11)
        self.multi_cell(0, 5, body)
        self.ln()

    def add_table(self, header, data, col_widths=None):
        self.set_font('Arial', 'B', 10)
        if col_widths is None:
            col_widths = [40] * len(header)
        
        # Header
        for i, h in enumerate(header):
            self.cell(col_widths[i], 7, str(h), 1, 0, 'C')
        self.ln()
        
        # Data
        self.set_font('Arial', '', 10)
        for row in data:
            for i, item in enumerate(row):
                self.cell(col_widths[i], 6, str(item), 1, 0, 'C')
            self.ln()

    def add_chart(self, chart_path, w=150):
        self.ln(5)
        self.image(chart_path, x=30, w=w)
        self.ln(5)

def generate_pdf_report(df, selected_years, tax_rate):
    pdf = PDFReport()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # Title Info
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1)
    if selected_years:
        period_str = ", ".join([f"FY{y}" for y in selected_years])
        pdf.cell(0, 10, f"Report Period: {period_str}", 0, 1)
    pdf.ln(5)

    # Process Data
    df['year'] = df['date'].dt.year
    df['fiscal_year'] = df['date'].apply(lambda x: x.year + 1 if x.month >= 4 else x.year)
    
    # Filter for selected years
    df_report = df[df['fiscal_year'].isin(selected_years)].copy()
    
    if df_report.empty:
        pdf.chapter_body("No data found for the selected period.")
        return pdf
    
    # Summary Table
    pdf.chapter_title("Financial Summary by Year")
    summary_data = []
    
    grouped = df_report.groupby('fiscal_year')
    for year, group in grouped:
        rev = group[group['amount'] > 0]['amount'].sum()
        exp = group[group['amount'] < 0]['amount'].sum()
        net = rev + exp
        tax = max(0, net * tax_rate)
        pat = net - tax
        
        summary_data.append([
            f"FY{year}",
            f"{rev:,.2f}",
            f"{abs(exp):,.2f}",
            f"{net:,.2f}",
            f"{tax:,.2f}",
            f"{pat:,.2f}"
        ])
        
    pdf.add_table(['Fiscal Year', 'Revenue', 'Expenses', 'Net Profit (Pre)', 'Tax', 'Net Profit (Post)'], 
                  summary_data, col_widths=[25, 32, 32, 35, 30, 35])
    pdf.ln(10)

    # Overall Trend Chart
    if len(selected_years) > 1:
        pdf.chapter_title("Multi-Year Trend")
        # Generate Chart
        trend_df = pd.DataFrame(summary_data, columns=['FY', 'Rev', 'Exp', 'Net', 'Tax', 'Pat'])
        # Convert back to numbers for plotting
        trend_df['Net Profit'] = trend_df['Net'].str.replace(',','').astype(float)
        trend_df['Post Tax'] = trend_df['Pat'].str.replace(',','').astype(float)
        
        plt.figure(figsize=(8, 4))
        plt.plot(trend_df['FY'], trend_df['Net Profit'], marker='o', label='Net Profit (Pre-Tax)')
        plt.plot(trend_df['FY'], trend_df['Post Tax'], marker='o', label='Net Profit (Post-Tax)')
        plt.title('Profit Trend')
        plt.legend()
        plt.grid(True)
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmpfile:
            plt.savefig(tmpfile.name)
            pdf.add_chart(tmpfile.name)
        plt.close()

    # Detailed Category Breakdown per Year
    for year in selected_years:
        pdf.add_page()
        pdf.chapter_title(f"Detailed Analysis for FY{year}")
        
        year_data = df_report[df_report['fiscal_year'] == year]
        
        # Monthly Trend Chart
        pdf.chapter_title("Monthly Net Profit Trend")
        monthly = year_data.copy()
        monthly['month_sort'] = monthly['date'].dt.to_period('M')
        monthly_group = monthly.groupby('month_sort')['amount'].sum().reset_index()
        monthly_group['month'] = monthly_group['month_sort'].astype(str)
        
        plt.figure(figsize=(10, 4))
        colors = ['g' if x >= 0 else 'r' for x in monthly_group['amount']]
        plt.bar(monthly_group['month'], monthly_group['amount'], color=colors)
        plt.xticks(rotation=45)
        plt.title(f"Monthly Net Profit - FY{year}")
        plt.tight_layout()
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmpfile:
            plt.savefig(tmpfile.name)
            pdf.add_chart(tmpfile.name, w=170)
        plt.close()

        # Category Pie Chart
        pdf.chapter_title("Expense Distribution")
        exp_data = year_data[year_data['amount'] < 0]
        cat_exp = exp_data.groupby('category')['amount'].apply(lambda x: abs(x.sum())).reset_index()
        
        if not cat_exp.empty:
            plt.figure(figsize=(6, 6))
            plt.pie(cat_exp['amount'], labels=cat_exp['category'], autopct='%1.1f%%', startangle=90)
            plt.title(f"Expense Breakdown - FY{year}")
            
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmpfile:
                plt.savefig(tmpfile.name)
                pdf.add_chart(tmpfile.name, w=120)
            plt.close()

        # Category Table
        pdf.ln(5)
        pdf.chapter_title("Category Table")
        cat_group = year_data.groupby(['category']).agg({'amount': 'sum'}).reset_index()
        cat_group['type'] = cat_group['amount'].apply(lambda x: 'Income' if x > 0 else 'Expense')
        cat_group = cat_group.sort_values(by=['type', 'amount'], ascending=[False, False])
        
        cat_data = []
        for _, row in cat_group.iterrows():
            cat_data.append([
                row['category'],
                row['type'],
                f"{abs(row['amount']):,.2f}"
            ])
            
        pdf.add_table(['Category', 'Type', 'Amount'], cat_data, col_widths=[80, 40, 50])

    return pdf
