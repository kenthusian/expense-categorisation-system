import pandas as pd  # type: ignore

class FinancialAdvisor:
    def __init__(self, df, salary=0):
        self.df = df
        self.salary = salary
        self.insights = []
        
    def analyze_50_30_20(self):
        """
        Analyzes spending based on 50/30/20 rule.
        Needs: Rent, Groceries, Utilities, Transport, Health
        Wants: Dining, Shopping, Entertainment, Travel
        """
        if self.df is None or self.df.empty:
            return None

        # Define categories (Lower case for matching)
        needs_cats = ['rent', 'housing', 'groceries', 'utilities', 'transport', 'health', 'insurance', 'education']
        wants_cats = ['dining', 'shopping', 'entertainment', 'travel', 'subscriptions', 'hobbies']
        
        # Calculate totals
        # Filter for expenses only (negative amounts usually, but we work with abs for classification)
        # Using strict category matching from our model
        
        expenses = self.df[self.df['category'] != 'Income'].copy()
        expenses['amount_abs'] = expenses['amount'].abs()
        expenses['cat_lower'] = expenses['category'].str.lower()
        
        total_needs = expenses[expenses['cat_lower'].isin(needs_cats)]['amount_abs'].sum()
        total_wants = expenses[expenses['cat_lower'].isin(wants_cats)]['amount_abs'].sum()
        
        # Catch-all for others (assume Want if not strictly Need? Or separate?)
        # Let's be strict. If it's not a Need, check if Want. If neither, classify as Want for safety or "Other"
        # Simplification: Everything not Need is a Want for this harsh advisor!
        # Actually better:
        
        actual_income = self.df[self.df['category'] == 'Income']['amount'].sum()
        income_to_use = actual_income if actual_income > 0 else self.salary
        
        # Savings is Income - Expenses (Net)
        total_expenses = expenses['amount_abs'].sum()
        savings = income_to_use - total_expenses
        
        # Recalculate 'Wants' as Total Expenses - Needs (captures everything else)
        total_wants = total_expenses - total_needs
        
        breakdown = {
            "Needs": {"amount": total_needs, "pct": (total_needs / income_to_use) * 100, "target": 50},
            "Wants": {"amount": total_wants, "pct": (total_wants / income_to_use) * 100, "target": 30},
            "Savings": {"amount": savings, "pct": (savings / income_to_use) * 100, "target": 20}
        }
        
        return breakdown

    def generate_actionable_insights(self):
        """
        Generates top 3 insights based on analysis.
        """
        breakdown = self.analyze_50_30_20()
        if not breakdown:
            return []
            
        insights = []
        
        # 1. Savings Check
        if breakdown['Savings']['pct'] < 20:
            shortfall = (0.20 * self.salary) - breakdown['Savings']['amount']
            insights.append({
                "type": "alert",
                "title": "Boost Savings",
                "text": f"You're saving {breakdown['Savings']['pct']:.1f}% (Target: 20%). Try to save {shortfall:.0f} more.",
                "action": "Check 'Cutting Expenses' tab"
            })
        else:
             insights.append({
                "type": "success",
                "title": "Savings on Track",
                "text": f"Great job! You're saving {breakdown['Savings']['pct']:.1f}% of income.",
                "action": "Consider Investing"
            })

        # 2. Needs Check
        if breakdown['Needs']['pct'] > 50:
             insights.append({
                "type": "warning",
                "title": "High Fixed Costs",
                "text": f"Needs are taking up {breakdown['Needs']['pct']:.1f}% of income (Target: 50%).",
                "action": "Review Rent/Utilities"
            })
            
        # 3. Wants Check (The "Cutting Spending" suggestions)
        if breakdown['Wants']['pct'] > 30:
             insights.append({
                "type": "alert",
                "title": "Overspending on Wants",
                "text": f"Wants are {breakdown['Wants']['pct']:.1f}% of income (Target: 30%).",
                "action": "Cut Dining/Shopping"
            })

        # 4. Waste Detection (High frequency, low amount)
        expenses = self.df[self.df['category'] != 'Income']
        if 'description' in expenses.columns:
            # Group by description to find recurring habits
            habits = expenses.groupby('description').filter(lambda x: len(x) > 4) # More than 4 times
        else:
             habits = pd.DataFrame()
        if not habits.empty:
            common_habit = habits.groupby('description')['amount'].sum().abs().sort_values(ascending=False).head(1)
            if not common_habit.empty:
                desc = common_habit.index[0]
                total = common_habit.values[0]
                insights.append({
                "type": "info",
                "title": "Habit Spotted",
                "text": f"You've spent {total:.0f} on '{desc}' recently.",
                "action": "Is this essential?"
            })
        
        return [insights[i] for i in range(min(len(insights), 3))]

    def get_combined_insights(self):
        """
        Combines 50/30/20 analysis with additional checks from reference logic.
        """
        insights = self.generate_actionable_insights()
        
        # 5. Category Concentration Check (From Reference)
        expenses = self.df[self.df['category'] != 'Income']
        if not expenses.empty:
            total_expense = expenses['amount'].abs().sum()
            cat_exp = expenses.groupby('category')['amount'].apply(lambda x: x.abs().sum())
            top_cat = cat_exp.idxmax()
            top_cat_pct = (cat_exp.max() / total_expense) * 100 if total_expense > 0 else 0
            
            if top_cat_pct > 40:
                insights.append({
                    "type": "info",
                    "title": "High Concentration",
                    "text": f"**{top_cat}** accounts for {top_cat_pct:.1f}% of your spending.",
                    "action": "Check details"
                })

        # 6. Anomaly Check (From Reference)
        if 'is_anomaly' in self.df.columns:
            anomalies = self.df[self.df['is_anomaly'] == -1] # Assuming -1 is anomaly based on model.py
            if not anomalies.empty:
                insights.append({
                    "type": "alert",
                    "title": "Anomalies Detected",
                    "text": f"Found {len(anomalies)} unusual transactions.",
                    "action": "Review Anomalies"
                })
                
        return insights
