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
        
        # 5. Category Concentration Check
        expenses = self.df[self.df['category'] != 'Income']
        if not expenses.empty:
            total_expense = expenses['amount'].abs().sum()
            cat_exp = expenses.groupby('category')['amount'].apply(lambda x: x.abs().sum())
            top_cat = cat_exp.idxmax()
            top_cat_pct = (cat_exp.max() / total_expense) * 100 if total_expense > 0 else 0
            
            if top_cat_pct > 35: # Tightened threshold for better focus
                insights.append({
                    "type": "info",
                    "title": f"Heavy {top_cat} Spending",
                    "text": f"Your spending is highly concentrated in {top_cat} ({top_cat_pct:.1f}% of budget). Reducing this by 10% would save you about ₹{(cat_exp.max() * 0.1):.0f} monthly.",
                    "action": "Check details"
                })

        # 6. Anomaly Check
        if 'is_anomaly' in self.df.columns:
            anomalies = self.df[self.df['is_anomaly'] == -1]
            if not anomalies.empty:
                insights.append({
                    "type": "alert",
                    "title": "Unusual Spending",
                    "text": f"Found {len(anomalies)} transactions that differ from your normal patterns. This might be a sign of leakage or fraud.",
                    "action": "Review Anomalies"
                })
        
        # 7. Surplus Check
        breakdown = self.analyze_50_30_20()
        if breakdown and breakdown['Savings']['amount'] > 0:
            surplus = breakdown['Savings']['amount']
            invested = self.df[self.df['category'].str.lower().str.contains('investment|sip|mutual fund|stock', na=False)]['amount'].abs().sum()
            if invested < (surplus * 0.5):
                to_invest = (surplus * 0.7) - invested
                if to_invest > 500:
                    insights.append({
                        "type": "success",
                        "title": "Idle Cash Detected",
                        "text": f"You have about ₹{surplus:,.0f} in surplus this month, but only ₹{invested:,.0f} is invested. You could put ₹{to_invest:,.0f} into an Index Fund today.",
                        "action": "Consider Investing"
                    })

        # 8. Discretionary Spending Check
        if breakdown:
            wants_pct = breakdown['Wants']['pct']
            if wants_pct > 35:
                potential_savings = breakdown['Wants']['amount'] * 0.2
                insights.append({
                    "type": "warning",
                    "title": "Lifestyle Inflation",
                    "text": f"Your 'Wants' are at {wants_pct:.1f}% of income. A 20% trim on non-essentials could add ₹{potential_savings:,.0f} to your wealth every month.",
                    "action": "Cut Dining/Shopping"
                })

        # 9. Cash Buffer (Burn Rate)
        expenses_df = self.df[self.df['category'] != 'Income']
        monthly_expense = expenses_df['amount'].abs().sum()
        actual_income = self.df[self.df['category'] == 'Income']['amount'].sum()
        income_to_use = actual_income if actual_income > 0 else self.salary
        
        if monthly_expense > 0:
            months_buffer = income_to_use / monthly_expense
            if months_buffer < 1.2:
                insights.append({
                    "type": "alert",
                    "title": "Tight Cash Flow",
                    "text": f"Your monthly expenses are very close to your income. You only have a {months_buffer:.1f}x coverage ratio. Consider building a larger buffer.",
                    "action": "Review Rent/Utilities"
                })
                
        return insights

    def get_investment_suggestions(self, health_details, score):
        """
        Generates deep, actionable investment suggestions based on health score details.
        """
        suggestions = []
        sr = health_details.get('savings_ratio', 0)
        ir = health_details.get('investment_ratio', 0)
        total_inv = health_details.get('total_invested', 0)
        net_savings = health_details.get('net_savings', 0)
        alloc = health_details.get('allocation', {})
        
        # 0. Prep metrics
        # Estimate monthly expenses from current data
        expenses_df = self.df[self.df['category'] != 'Income']
        monthly_expense = expenses_df['amount'].abs().sum() if not expenses_df.empty else (self.salary * 0.7)
        
        # 1. Emergency Fund (Data-Driven Target)
        ef_target = monthly_expense * 6
        if total_inv < ef_target:
            shortfall = ef_target - total_inv
            suggestions.append({
                "icon": "🛡️", "title": f"Foundation: Build ₹{ef_target/1000:,.0f}k Emergency Fund",
                "desc": f"Your current monthly expenses are approx ₹{monthly_expense:,.0f}. Aim for a 6-month buffer of ₹{ef_target:,.0f}. You are currently ₹{shortfall:,.0f} short. Keep this in a Liquid Fund for 24/7 access."
            })
        
        # 2. SIP Strategy (Surplus-Driven)
        surplus = max(0, net_savings)
        if surplus > 5000:
            sip_aim = surplus * 0.6
            suggestions.append({
                "icon": "📈", "title": f"Start a ₹{sip_aim:,.0f}/mo SIP",
                "desc": f"Since you have a monthly surplus of ₹{surplus:,.0f}, you can comfortably automate ₹{sip_aim:,.0f} into a Nifty 50 Index Fund. Compounding works best when it's consistent!"
            })

        # 3. Tax Saving (Indian 80C Focus)
        if self.salary > 41000: # Over 5LPA
            suggestions.append({
                "icon": "⚖️", "title": "Tax Optimization (80C/NPS)",
                "desc": "Use ELSS Mutual Funds for the shortest lock-in (3yr) or PPF for risk-free 7%+ returns. Also, add ₹50k to NPS for additional tax savings under 80CCD."
            })

        # 4. Asset Allocation Correction
        stocks_pct = alloc.get('stocks', 0)
        if stocks_pct > 75:
            suggestions.append({
                "icon": "⚓", "title": "De-risk: Add Stability",
                "desc": "Your portfolio is aggressive (>75% Equity). Balance it by moving some surplus to Sovereign Gold Bonds (SGB) or Debt Funds. Gold adds a great cushion during market crashes."
            })
        elif stocks_pct < 40 and total_inv > 50000:
            suggestions.append({
                "icon": "🚀", "title": "Growth: Increase Equity",
                "desc": f"At {stocks_pct:.1f}% equity, you might struggle to beat inflation. Gradually increase exposure to Mid-cap or Flexi-cap funds to target 12-14% long-term returns."
            })

        # 5. Advanced Milestones
        if total_inv > 1000000:
            suggestions.append({
                "icon": "🏘️", "title": "HNI Diversification: REITs",
                "desc": "With a 10L+ portfolio, look at REITs (Real Estate Investment Trusts) to get commercial property exposure and quarterly dividends without the hassle of physical real estate."
            })
            
        # 6. Insurance Check (Humane addition)
        suggestions.append({
            "icon": "🩺", "title": "Health First",
            "desc": "No investment plan is complete without safety. Ensure your Health Insurance cover is at least 10x your monthly expense to protect your principal during a crisis."
        })

        if not suggestions:
            suggestions.append({
                "icon": "✨", "title": "Elite Discipline",
                "desc": "Your metrics are perfect. Focus now on Estate Planning (Nominations, Wills) and ensuring your Health & Term Insurance cover is at least 20x your annual income."
            })
            
        return suggestions
