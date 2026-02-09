import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd

def render_charts(df):
    """
    Renders charts based on the dataframe.
    """
    if 'category' not in df.columns:
        st.warning("No category column found for visualization.")
        return

    # 1. Pie Chart of Expenses by Category
    st.subheader("Expenses by Category")
    
    # Filter out Income if possible? For now verify what's there
    # Assuming positive/negative amounts, or just categorize everything
    
    category_counts = df['category'].value_counts()
    
    fig1, ax1 = plt.subplots()
    ax1.pie(category_counts, labels=category_counts.index, autopct='%1.1f%%', startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    st.pyplot(fig1)

    # 2. Bar Chart
    st.subheader("Transaction Counts by Category")
    st.bar_chart(category_counts)
