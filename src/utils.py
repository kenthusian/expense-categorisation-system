import altair as alt
import streamlit as st
import pandas as pd
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
        
        with open(file_path, 'r') as f:
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
